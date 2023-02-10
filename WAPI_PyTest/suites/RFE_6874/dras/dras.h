/*
*  $Id: dras.c,v 1.84 2008/08/14 01:45:01 roberts Exp $
*  DHCP load generator
*
*
*/
#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <unistd.h>
#include <string.h>
#include <ctype.h>
#include <stdint.h>
#include <signal.h>
#include <time.h>
#include <assert.h>
#include <sys/time.h>
#include <sys/types.h>
#ifdef linux
#include <sys/ioctl.h>
#endif
#include <poll.h>
#include <sys/socket.h>
#include <sys/queue.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#include "dhcp.h"
/* Local Definitions */

typedef struct {
    uint32_t offer_latency_avg;
    uint32_t offer_latency_min;
    uint32_t offer_latency_max;
    uint32_t ack_latency_avg;
    uint32_t ack_latency_min;
    uint32_t ack_latency_max;
    uint32_t discoveries_sent;
    uint32_t requests_sent;
    uint32_t releases_sent;
    uint32_t informs_sent;
    uint32_t leaseq_sent;
    uint32_t discover_rate_avg;
    uint32_t offers_received;
    uint32_t acks_received;
    uint32_t naks_received;
    uint32_t acks_last;
    uint32_t offer_timeouts;
    uint32_t ack_timeouts;
    uint32_t errors;
    uint32_t failed;
    uint32_t completed;
} dhcp_stats_t;

typedef struct dhcp_option {
    int option_no;
    int data_len;
    int discover_only;
    char *data;
    struct dhcp_option *next;
} DHCP_OPTION;

typedef struct dhcp_session_t {
    TAILQ_ENTRY(dhcp_session_t) link;
    uint32_t xid;
    in_addr_t yiaddr;
    in_addr_t ciaddr;
    in_addr_t server_id;
    uint32_t giaddr;
    uint8_t mac[6];
    uint16_t start_from;
    char hostname[32];
    uint8_t options[DHCP_MAX_OPTION_LEN];
    DHCP_OPTION *extra_options;
    uint8_t options_length;
    uint32_t timeouts;
    uint32_t naks;
    uint32_t lease_time;
    uint32_t session_start;
    struct timeval time_sent;
    struct timeval time_received;
    uint8_t  type_sent;
    uint8_t  type_received;
} dhcp_session_t;

typedef struct DHCP_SERVER_T {
    struct sockaddr_in sa;
    dhcp_stats_t stats;
    dhcp_stats_t peer_stats;	  /* Failover peer stats */
    struct sockaddr_in fa;	  /* Failover assoc peer sock addr */
    int failover;
    dhcp_session_t *list;
    uint32_t active;
    struct timeval first_packet_sent;
    struct timeval last_packet_sent;
    struct timeval last_packet_received;
    struct timeval last_stat;
    TAILQ_HEAD(, dhcp_session_t) q_free;
    TAILQ_HEAD(, dhcp_session_t) q_inuse;
    struct DHCP_SERVER_T *next;
} dhcp_server_t;

typedef struct LEASE_DATA_T {
    uint8_t mac[6];
    uint16_t start_from;
    in_addr_t ipaddr;
    char *hostname;
    in_addr_t server_id;
    DHCP_OPTION *options;
    uint32_t giaddr;
    struct LEASE_DATA_T *next;
} lease_data_t;

typedef struct {
    int send_remote_id;
    int send_circuit_id;
    char *remote_id;
    char *circuit_id;
    struct in_addr link_selection;
    struct in_addr server_id_override;
} ra_subopts_t;

#define BOOTP_REQUEST		16
#define BOOTP_REPLY		17

#define WINOPTIONS "\x37\x0c\x01\x0f\x03\x06\x2c\x2e\x2f\x1f\x21\x2b\x5f\x96\xff\x00"
#define WINOPTIONLEN 16
#define SOPT81       1
#define OOPT81       2
#define EOPT81       4
#define NOPT81       8

#define MAX_TOKENS   64

#define DELTATV(a,b)  (1000000*(a.tv_sec - b.tv_sec) + a.tv_usec - b.tv_usec)
#define DELTATVS(a,b)  ((double)a.tv_sec - (double)b.tv_sec + ((double)a.tv_usec - (double)b.tv_usec)/1000000)
#define TVSET(a,b) (a.tv_sec = b.tv_sec, a.tv_usec = b.tv_usec)
#define TVZERO(a) (a.tv_sec = 0, a.tv_usec = 0)

#ifndef TAILQ_FOREACH_SAFE
#define TAILQ_FOREACH_SAFE(var, head, field, tvar)           \
        for ((var) = TAILQ_FIRST((head));                    \
            (var) && ((tvar) = TAILQ_NEXT((var), field), 1); \
            (var) = (tvar))
#endif

/* Globals */
static char *version = "$Id: dras.c,v 1.84 2008/08/14 01:45:01 roberts Exp $";
static int broadcast;
static int bootp;
static int use_sequential_mac;
static int random_mac;
static int send_hostname;
static int stats_interval;
static int send_opt81;
static int send_opt61;
static int send_opt50;
static int no_opt_req;
static char *opt61_string;
static int opt61_strlen;
static ra_subopts_t *opt82_subopts = NULL;
static int random_hostname;
static uint32_t socket_bufsize = 128 * 1024;
static double target_rate;
static uint32_t test_length;
static uint32_t xid = 1;
static uint16_t secs_offset;
static int send_release;
static int send_inform;
static int retransmit;
static int dhcp_ping;
static int renew_lease;
static int renew_both_peers;
static int parse;
static int send_until_answered;
static int verbose = 0;
static int server_port = 67;
static int sock = -1;
static double timeout = 5.;
static int number_requests = 1;
static uint8_t firstmac[6];
static uint32_t max_sessions = 25;
static uint8_t flags81;
static dhcp_server_t *servers;
static uint32_t num_servers;
static struct in_addr srcaddr = { INADDR_ANY };
static pid_t pid;
static char *logfile;
static char *input_file;
static char *output_file;
static char *domain81;
static int hwlen_zero;
#ifdef PCAP
static char *ifname;
#endif
static int domain81_len;
FILE *logfp;
static FILE *outfp;
static struct timeval start_time;
static uint32_t total_completed;
static uint32_t total_failed;

static DHCP_OPTION *extraoptions;

/* Function prototypes */
static int reader(void);
static void sender(void);
inline void free_session(dhcp_server_t *, dhcp_session_t *);
static int process_packet(struct dhcp_packet *, struct timeval *, uint32_t);
static int send_packet(int, dhcp_session_t *, dhcp_server_t *);
static void parse_args(int, char **);
static int add_servers(const char *);
static int read_lease_data(lease_data_t **);
static void usage(void);
static int process_sessions(void);
static void print_packet(size_t, struct dhcp_packet *);
static int test_statistics(void);
static char *unpack81(uint8_t *);
static int pack81(uint8_t *, const char *);
static int parse81(char *);
static int parse82(char *);
static inline void getmac(uint8_t *);
inline char *addrtoa(uint32_t, char *buf);
static uint32_t get_local_addr(void);
static DHCP_OPTION *addoption(int, char *, DHCP_OPTION **);
int get_tokens(char *, char **, int);
int dras_sendto(uint8_t *, int, uint32_t, struct sockaddr_in *);
void print_lease(FILE *, dhcp_session_t *);
int pack61(uint8_t *, dhcp_session_t *);
static int pack82(uint8_t *, dhcp_session_t *);
static void fill_session(lease_data_t *, dhcp_session_t *);
#ifdef PCAP
int init_rawnet(char *, uint32_t, uint32_t);
int send_raw(u_char *, size_t, uint32_t, uint32_t);
int receive_pcap(u_char *, struct timeval *);
#endif

