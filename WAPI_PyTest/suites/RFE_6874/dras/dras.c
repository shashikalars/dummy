#include "dras.h"


int main(int argc, char **argv) {
    struct sockaddr_in ca;
    int i, ret, flag = 1;
    dhcp_server_t *server;

    logfp = stderr;
    gettimeofday(&start_time, NULL);
    parse_args(argc, argv);
#ifndef __CYGWIN__
    if (getuid()) {
        fprintf(stderr, "\n\tThis program must be run as root\n");
        exit(1);
    }
#endif
    pid = getpid();
    srand(pid + time(NULL));

    if (logfile != NULL) {
        logfp = fopen(logfile, "w");
        if (logfp == NULL) {
            fprintf(stderr, "Open %s failed\n", logfile);
            exit(1);
        }
        setvbuf(logfp, NULL, _IONBF, 0);
    }
    else
        logfp = stderr;

    if (!parse)
        fprintf(logfp, "Begin: Version %s\n", version);

    if (output_file != NULL) {
        outfp = fopen(output_file, "w");
        if (outfp == NULL) {
            fprintf(logfp, "Open failed: %s\n", output_file);
            exit(1);
        }
        setvbuf(outfp, NULL, _IONBF, 0);
    }

    if ((!broadcast) && (srcaddr.s_addr == INADDR_ANY))
        srcaddr.s_addr = get_local_addr();

    signal(SIGPIPE, SIG_IGN);

#ifdef PCAP
    if (ifname) {
        if ((sock = init_rawnet(ifname, broadcast ? server_port + 1 : server_port, server_port)) < 0) {
            fprintf(logfp, "init_ifname failed\n");
            exit(1);
        }
    } else {
#endif
    sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (sock < 0) {
        perror("socket:");
        exit(1);
    }

    if (broadcast) {
        if (setsockopt(sock, SOL_SOCKET, SO_BROADCAST, (char *)&flag, sizeof(flag)) < 0) {
            perror("setsockopt");
            exit(1);
        }
    }

    ret = setsockopt(sock, SOL_SOCKET, SO_RCVBUF, (char *)&socket_bufsize, sizeof(socket_bufsize));
    if (ret < 0)
        fprintf(stderr, "Warning:  setsockbuf(SO_RCVBUF) failed\n");

    ret = setsockopt(sock, SOL_SOCKET, SO_SNDBUF, (char *)&socket_bufsize, sizeof(socket_bufsize));
    if (ret < 0)
        fprintf(stderr, "Warning:  setsockbuf(SO_SNDBUF) failed\n");

    memset(&ca, 0, sizeof(struct sockaddr_in));
    ca.sin_family = AF_INET;

    if (broadcast)
        ca.sin_port = htons(server_port + 1);
    else
        ca.sin_port = htons(server_port);

    memcpy(&ca.sin_addr, &srcaddr, sizeof(struct in_addr));
    if (bind(sock, (struct sockaddr *) &ca, sizeof(ca)) < 0) {
        perror("bind");
        exit(1);
    }
#ifdef PCAP
    }
#endif

    for (server = servers; server != NULL; server = server->next) {
        server->list = calloc(max_sessions, sizeof(dhcp_session_t));
        TAILQ_INIT(&server->q_free);
        TAILQ_INIT(&server->q_inuse);
        for (i = 0; i < max_sessions; i++)
            TAILQ_INSERT_TAIL(&server->q_free, &server->list[i], link);

        server->sa.sin_port = htons(server_port);
        if (server->failover)
            server->fa.sin_port = htons(server_port);
    }

    if (!parse && use_sequential_mac)
        fprintf(logfp, "First MAC:            %02x:%02x:%02x:%02x:%02x:%02x\n",
                firstmac[0], firstmac[1], firstmac[2],
                firstmac[3], firstmac[4], firstmac[5]);

    sender();
    return(test_statistics());
}

// Test is complete when sessions_started = completed + timeouts
void sender(void) {
    double rate;
    int n = 0;
    uint32_t sessions_started = 0;
    dhcp_session_t *session;
    dhcp_server_t *current_server = servers;
    lease_data_t *leases = NULL;
    lease_data_t *lease;
    struct timespec ts_sleep;
    static struct timeval now, then;

    if (input_file != NULL && (number_requests = read_lease_data(&leases)) < 0)
        exit(1);

    lease = leases;
    if (target_rate) {
        if (!parse)
            fprintf(logfp, "Target rate:          %.1f leases/sec\n", target_rate);

        ts_sleep.tv_nsec = 1e8 / target_rate;
        ts_sleep.tv_sec = 0;
        if (ts_sleep.tv_nsec > 1e9) {
            ts_sleep.tv_sec = ts_sleep.tv_nsec / 1e9;
            ts_sleep.tv_nsec = 1 + ts_sleep.tv_nsec - 1e9 * ts_sleep.tv_sec;
        }

        gettimeofday(&then, NULL);
    }

    while (total_completed + total_failed < number_requests) {
        if (lease != NULL && lease->server_id != 0) {
            dhcp_server_t *s;

            for (s = servers; s != NULL; s = s->next) {
                if (s->sa.sin_addr.s_addr == lease->server_id) {
                    current_server = s;
                    break;
                }
            }
        }

        if (sessions_started < number_requests &&
            (session = TAILQ_FIRST(&current_server->q_free)) != NULL) {

            TAILQ_REMOVE(&current_server->q_free, session, link);
            TAILQ_INSERT_TAIL(&current_server->q_inuse, session, link);
            current_server->active++;
            gettimeofday(&now, NULL);

            if (target_rate) {
                n++;
                if (n == 23) {
                    n = 0;
                    rate = 23. / DELTATVS(now, then);

                    if (rate > target_rate)
                        ts_sleep.tv_nsec += 2e9 / target_rate - 2e9 / rate;
                    else
                        ts_sleep.tv_nsec = 0;

                    if (ts_sleep.tv_nsec > 1e9) {
                        ts_sleep.tv_sec = ts_sleep.tv_nsec / 1e9;
                        ts_sleep.tv_nsec =  1 + ts_sleep.tv_nsec - 1e9 * ts_sleep.tv_sec;
                    }

                    TVSET(then, now);
                }

                if (ts_sleep.tv_nsec > 0)
                    nanosleep(&ts_sleep, NULL);
            }

            if (input_file != NULL) {
                if (lease != NULL) {
                    fill_session(lease, session);
                    send_packet(lease->start_from, session, current_server);
                    lease = lease->next;
                }
            }
            else {
                fill_session(NULL, session);
                if (send_inform)
                    send_packet(DHCPINFORM, session, current_server);
                else
                    send_packet(DHCPDISCOVER, session, current_server);
            }

            sessions_started++;
        }
        else {
            if (num_servers > 1 && use_sequential_mac)
                getmac(NULL);    /* keep MAC allocation constant */

            process_sessions();
        }

        reader();

        if (current_server->next == NULL)
            current_server = servers;
        else
            current_server = current_server->next;

        if ((test_length > 0) && (DELTATVS(now, start_time) > test_length))
            return;
    }
}

void fill_session(lease_data_t *lease, dhcp_session_t *session) {
    if (lease != NULL) {
        session->xid = xid++;
        if (random_mac) //If '-e' then randomize the MAC
            getmac(session->mac);
        else
            memcpy(session->mac, lease->mac, 6);

        session->extra_options = lease->options;
        session->giaddr = lease->giaddr;
        session->yiaddr = lease->ipaddr;
        session->start_from = lease->start_from;

        if (!bootp) {
            if (lease->start_from == DHCPREQUEST) {
                session->type_sent = DHCPDISCOVER;
                session->type_received = DHCPOFFER;
                memcpy(session->options, "\x35\x01\x03", 3);
                session->options_length += 3;
            }

            if (!no_opt_req) {
                memcpy(session->options + 3, WINOPTIONS, WINOPTIONLEN);
                session->options_length += WINOPTIONLEN;
            }
        }

        session->server_id = lease->server_id;
        if (lease->hostname != NULL)
            strncpy(session->hostname, lease->hostname, 32);
        else {
            if (send_hostname || send_opt81) {
                if (random_hostname)
                    sprintf(session->hostname, "h%u%u", rand(), rand());
                else
                    sprintf(session->hostname, "h%02x%02x%02x%02x%02x%02x",
                            session->mac[0], session->mac[1], session->mac[2],
                            session->mac[3], session->mac[4], session->mac[5]);
            }
            else
                *(session->hostname) = '\0';
        }
    }
    else {
        getmac(session->mac);

        session->extra_options = extraoptions;
        session->xid = xid++;
        session->giaddr = srcaddr.s_addr;
        if (send_hostname || send_opt81) {
            if (random_hostname)
                sprintf(session->hostname, "h%u%u", rand(), rand());
            else
                sprintf(session->hostname, "h%02x%02x%02x%02x%02x%02x",
                        session->mac[0], session->mac[1], session->mac[2],
                        session->mac[3], session->mac[4], session->mac[5]);
        }
        else
            *(session->hostname) = '\0';
    }
}

int test_statistics(void) {
    dhcp_server_t *iter;
    double elapsed;
    int retval = 0;

    if (parse) {
        for (iter = servers; iter != NULL; iter = iter->next) {
            fprintf(logfp, "%s %ld", inet_ntoa(iter->sa.sin_addr), start_time.tv_sec);
            if (iter->stats.offers_received + iter->stats.acks_received + iter->stats.naks_received +
                iter->peer_stats.acks_received + iter->peer_stats.offers_received == 0) {
                fprintf(logfp, " no replies received.\n");
                retval = 1;
                continue;
            }

            if (iter->stats.failed + iter->stats.errors > 0)
                retval = 1;

            elapsed = DELTATVS(iter->last_packet_received, iter->first_packet_sent);
            fprintf(logfp, " t %.6f d %u o %u %.3f %.3f r %u a %d %.3f %.3f N %d R %d oto %u ato %u comp %u fail %u err %u\n",
                    elapsed, iter->stats.discoveries_sent, iter->stats.offers_received, iter->stats.offers_received / elapsed,
                    0.0010 * (double) iter->stats.offer_latency_avg / (double) (iter->stats.offers_received ? iter->stats.offers_received : 1),
                    iter->stats.requests_sent, iter->stats.acks_received, iter->stats.acks_received / elapsed,
                    0.0010 * (double) iter->stats.ack_latency_avg / (double) (iter->stats.acks_received ? iter->stats.acks_received : 1),
                    iter->stats.naks_received, iter->stats.releases_sent, iter->stats.offer_timeouts, iter->stats.ack_timeouts,
                    iter->stats.completed, iter->stats.failed, iter->stats.errors);
        }
    }
    else {
        fprintf(logfp, "\nTest started:         %s\n", ctime(&start_time.tv_sec));
        for (iter = servers; iter != NULL; iter = iter->next) {
            fprintf(logfp, "Server:             %-s\n", inet_ntoa(iter->sa.sin_addr));

            if (iter->stats.offers_received + iter->stats.acks_received + iter->stats.naks_received +
                iter->peer_stats.acks_received + iter->peer_stats.offers_received == 0) {
                fprintf(logfp, "\n\tNo replies received.\n");
                retval = 1;
                continue;
            }

            if (iter->stats.failed + iter->stats.errors > 0)
                retval = 1;

            fprintf(logfp, "Discoveries sent: %6u\n", iter->stats.discoveries_sent);
            fprintf(logfp, "Offers Received:  %6u\n", iter->stats.offers_received);
            fprintf(logfp, "Requests sent:    %6u\n", iter->stats.requests_sent);
            fprintf(logfp, "Informs sent:     %6u\n", iter->stats.informs_sent);
            fprintf(logfp, "Acks Received:    %6u\n", iter->stats.acks_received);
            fprintf(logfp, "Naks received:    %6u\n", iter->stats.naks_received);
            fprintf(logfp, "Releases sent:    %6u\n", iter->stats.releases_sent);
            fprintf(logfp, "Offer timeouts:   %6u\n", iter->stats.offer_timeouts);
            fprintf(logfp, "ACK Timeouts:     %6u\n", iter->stats.ack_timeouts);

            elapsed = DELTATVS(iter->last_packet_received, iter->first_packet_sent);
            if (elapsed < 0) {
                fprintf(logfp, "Elapsed time went negative.  Aborting\n");
                exit(1);
            }

            fprintf(logfp, "Completed:        %6u\n", iter->stats.completed);
            fprintf(logfp, "Failed:           %6u\n", iter->stats.failed);
            fprintf(logfp, "Errors:           %6u\n", iter->stats.errors);
            fprintf(logfp, "Elapsed time:     %16.3f secs\n", elapsed);
            fprintf(logfp, "Offer Latency (Min/Max/Avg): %.3f/%.3f/%.3f (ms)\n",
                    0.0010 * (double) iter->stats.offer_latency_min,
                    0.0010 * (double) iter->stats.offer_latency_max,
                    0.0010 * (double) iter->stats.offer_latency_avg /
                    (double) (iter->stats.offers_received ? iter->stats.offers_received : 1));
            fprintf(logfp, "Ack Latency (Min/Max/Avg):   %.3f/%.3f/%.3f (ms)\n",
                    0.0010 * (double) iter->stats.ack_latency_min,
                    0.0010 * (double) iter->stats.ack_latency_max,
                    0.0010 * (double) iter->stats.ack_latency_avg /
                    (double) (iter->stats.acks_received ? iter->stats.acks_received : 1));
            fprintf(logfp, "Offers/sec:                  %6.2f\n",
                    (double) iter->stats.offers_received / elapsed);
            fprintf(logfp, "Leases/sec:                  %6.2f\n",
                    (double) iter->stats.acks_received / elapsed);

            if (iter->failover == 0) {
                fprintf(logfp, "-----------------------------------------\n");
                continue;
            }

            fprintf(logfp, "\nFailover Peer: %16s\n", inet_ntoa(iter->fa.sin_addr));
            if (iter->peer_stats.offers_received +
                iter->peer_stats.acks_received + iter->peer_stats.naks_received == 0) {
                fprintf(logfp, "\n\tNo replies received.\n");
                continue;
            }

            fprintf(logfp, "Offers Received:  %6u\n", iter->peer_stats.offers_received);
            fprintf(logfp, "Acks received:    %6u\n", iter->peer_stats.acks_received);
            fprintf(logfp, "Naks received:    %6u\n", iter->peer_stats.naks_received);
            fprintf(logfp, "Offer Latency (Min/Max/Avg): %.3f/%.3f/%.3f (ms)\n",
                    0.0010 * (double) iter->peer_stats.offer_latency_min,
                    0.0010 * (double) iter->peer_stats.offer_latency_max,
                    0.0010 * (double) iter->peer_stats.offer_latency_avg /
                    (double) (iter->peer_stats.offers_received ? iter->peer_stats.offers_received : 1));
            fprintf(logfp, "Ack Latency (Min/Max/Avg):   %.3f/%.3f/%.3f (ms)\n",
                    0.0010 * (double) iter->peer_stats.ack_latency_min,
                    0.0010 * (double) iter->peer_stats.ack_latency_max,
                    0.0010 * (double) iter->peer_stats.ack_latency_avg /
                    (double) (iter->peer_stats.acks_received ? iter->peer_stats.acks_received : 1));
            fprintf(logfp, "Offers/sec:      %17.2f\n",
                    (double) iter->peer_stats.offers_received / elapsed);
            fprintf(logfp, "Leases/sec:      %17.2f\n",
                    (double) iter->peer_stats.acks_received / elapsed);
            fprintf(logfp, "-----------------------------------------\n");
            fprintf(logfp, "Total Leases/sec:      %11.2f\n",
                    (double) iter->stats.completed / elapsed);
            if (iter->next != NULL)
                fprintf(logfp, "-----------------------------------------\n");
        }
    }

    if (!parse)
        fprintf(logfp, "Return value: %d\n", retval);

    return(retval);
}

int send_packet(int type, dhcp_session_t *session, dhcp_server_t *server) {
    static uint8_t buffer[1472];        /* Fix to DHCP_MTU */
    struct dhcp_packet *packet;
    struct timeval timestamp;
    int hostlen = 0, offset = 0;
    size_t packlen = 0;
    DHCP_OPTION *popt;

    packet = (struct dhcp_packet *) buffer;
    packet->op = 1;        /* Boot request */
    packet->xid = htonl(session->xid);
    packet->ciaddr.s_addr = 0;

    if (broadcast)
        packet->flags = htons(BOOTP_BROADCAST);
    else {
        if (renew_both_peers && !send_opt50)
            packet->flags = htons(BOOTP_BROADCAST);

        packet->hops = 1;
        packet->giaddr.s_addr = session->giaddr;
    }

    packet->htype = 1;        /* Ethernet */
    if (hwlen_zero)
        packet->hlen = 0;
    else
        packet->hlen = 6;

    memcpy(packet->chaddr, session->mac, 6);
    if (!bootp) {
        memcpy(packet->options, DHCP_OPTIONS_COOKIE, 4);
        offset = 4;
    }

    packet->ciaddr.s_addr = session->yiaddr;
    if (bootp)
        packlen = DHCP_FIXED_NON_UDP + 64;
    else if (type == DHCPDISCOVER) {
        *(packet->options + offset++) = DHO_DHCP_MESSAGE_TYPE;
        *(packet->options + offset++) = 1;
        *(packet->options + offset++) = DHCPDISCOVER;

        if (send_opt61)
            offset += pack61(packet->options + offset, session);

        if (opt82_subopts)
            offset += pack82(packet->options + offset, session);

        if (session->extra_options) {
            for (popt = session->extra_options; popt; popt = popt->next) {
                *(packet->options + offset++) = (char) popt->option_no;
                *(packet->options + offset++) = (char) popt->data_len;
                memcpy(packet->options + offset, popt->data, popt->data_len);
                offset += popt->data_len;
            }
        }

        if (!no_opt_req) {
            memcpy(packet->options + offset, WINOPTIONS, WINOPTIONLEN);
            offset += WINOPTIONLEN;
        }

        packlen = DHCP_FIXED_NON_UDP + offset;
    }
    else if (type == DHCPREQUEST) {    /* DHCP Request type converted in process */
        if (*(session->hostname) != '\0') {
            hostlen = strlen(session->hostname);

            if (send_opt81)
                offset += pack81(packet->options + offset, session->hostname);

            if (send_hostname) {    /* Apparently, some clients do both */
                *(packet->options + offset++) = DHO_HOST_NAME;
                *(packet->options + offset++) = hostlen;
                memcpy(packet->options + offset, session->hostname, hostlen);
                offset += hostlen;
            }
        }

        if (send_opt61)
            offset += pack61(packet->options + offset, session);

        if (opt82_subopts)
            offset += pack82(packet->options + offset, session);

        if (session->extra_options) {
            for (popt = session->extra_options; popt; popt = popt->next) {
                if (popt->discover_only)
                    continue;

                *(packet->options + offset++) = (char) popt->option_no;
                *(packet->options + offset++) = (char) popt->data_len;
                memcpy(packet->options + offset, popt->data, popt->data_len);
                offset += popt->data_len;
            }
        }

        if ((!renew_lease) || (renew_lease && send_opt50)) {
            packet->ciaddr.s_addr = 0;
            *(packet->options + offset++) = DHO_DHCP_REQUESTED_ADDRESS;
            *(packet->options + offset++) = 4;
            memcpy(packet->options + offset, &session->yiaddr, 4);
            offset += 4;
        }

        memcpy(packet->options + offset, session->options, session->options_length);
        offset += session->options_length;
        *(packet->options + offset++) = DHO_END;
        *(packet->options + offset++) = DHO_PAD;
        packlen = DHCP_FIXED_NON_UDP + offset + session->options_length;
    }
    else if (type == DHCPINFORM) {
        *(packet->options + offset++) = DHO_DHCP_MESSAGE_TYPE;
        *(packet->options + offset++) = 1;
        *(packet->options + offset++) = DHCPINFORM;

        memcpy(packet->options + offset, WINOPTIONS, WINOPTIONLEN);
        offset += WINOPTIONLEN;
//        if (session->extra_options) {
//            for (popt = session->extra_options; popt; popt = popt->next) {
//                *(packet->options + offset++) = (char) popt->option_no;
//                *(packet->options + offset++) = (char) popt->data_len;
//                memcpy(packet->options + offset, popt->data, popt->data_len);
//                offset += popt->data_len;
//            }
//        }

        memcpy(packet->options + offset, session->options, session->options_length);
        offset += session->options_length;
        *(packet->options + offset++) = DHO_END;
        *(packet->options + offset++) = DHO_PAD;
        packlen = DHCP_FIXED_NON_UDP + offset + session->options_length;
    }
    else if (type == DHCPRELEASE) {
        packet->ciaddr.s_addr = session->yiaddr;
        memcpy(packet->options + 4, "\x35\x01\x07\xff\x00", 5);
        packlen = DHCP_FIXED_NON_UDP + 4 + 5;
    }
    else if (type == DHCPLEASEQUERY) {
        packet->htype = 0;
        packet->hlen = 0;
        memset(packet->chaddr, 0, 6);
        packet->ciaddr.s_addr = session->yiaddr;
        memcpy(packet->options + 4, "\x35\x01\x0a\xff\x00", 5);
        packlen = DHCP_FIXED_NON_UDP + 4 + 5;
    }
    else {
        fprintf(logfp, "\n\tUnsupported packet type: %d\n", type);
        exit(1);
    }

    gettimeofday(&timestamp, NULL);
    TVSET(server->last_packet_sent, timestamp);
    TVSET(session->time_sent, timestamp);
    session->type_sent = type;

    if (session->session_start == 0)
        session->session_start = timestamp.tv_sec;
    else
        packet->secs = htons(timestamp.tv_sec - session->session_start + secs_offset);

    // If failover association and server_id is set then send to only that server.
    if (server->failover == 0 || broadcast != 0) {
        if (dras_sendto(buffer, packlen, session->giaddr, &server->sa) < 0)
            return(-1);
    }
    else {
        if (type == DHCPDISCOVER || session->server_id == 0 || renew_both_peers) {
            if (dras_sendto(buffer, packlen, session->giaddr, &server->sa) < 0)
                return(-1);

            if (dras_sendto(buffer, packlen, session->giaddr, &server->fa) < 0)
                return(-1);
        }
        else if (session->server_id == server->fa.sin_addr.s_addr) {
            if (dras_sendto(buffer, packlen, session->giaddr, &server->fa) < 0)
                return(-1);
        }
        else {
            if (dras_sendto(buffer, packlen, session->giaddr, &server->sa) < 0)
                return(-1);
        }
    }

    if (server->first_packet_sent.tv_sec == 0)
        TVSET(server->first_packet_sent, timestamp);

    if (bootp)
        server->stats.discoveries_sent++;
    else if (type == DHCPDISCOVER)
        server->stats.discoveries_sent++;
    else if (type == DHCPREQUEST)
        server->stats.requests_sent++;
    else if (type == DHCPINFORM)
        server->stats.informs_sent++;
    else if (type == DHCPLEASEQUERY)
        server->stats.leaseq_sent++;
    else if (type == DHCPRELEASE) {
        server->stats.releases_sent++;
        server->stats.completed++;
        total_completed++;
        free_session(server, session);
    }

    return(0);
}

int dras_sendto(uint8_t *packet, int len, uint32_t source, struct sockaddr_in *sa) {
    if (verbose > 1)
        print_packet(len, (struct dhcp_packet *)packet);

#ifdef PCAP
    if (ifname) {
        if (send_raw(packet, len, source, sa->sin_addr.s_addr) < 0) {
            fprintf(logfp, "send_raw failed:\n");
            return(-1);
        }
    }
    else {
#endif
        if (sendto(sock, packet, len, 0, (struct sockaddr *) sa, sizeof(struct sockaddr_in)) < 0) {
            fprintf(logfp, "sendto failed:\n");
            return(-1);
        }
#ifdef PCAP
    }
#endif

    return(0);
}

int process_sessions(void) {
    dhcp_session_t *session, *ts;
    dhcp_server_t *server;
    struct timeval now;

    gettimeofday(&now, NULL);
    for (server = servers; server != NULL; server = server->next) {
        TAILQ_FOREACH_SAFE(session, &server->q_inuse, link, ts) {
            if (DELTATVS(now, session->time_sent) > timeout) {
                // Should we add DHCPINFORM timeout counting ??
                if (session->type_sent == DHCPDISCOVER)
                    server->stats.offer_timeouts++;
                else
                    server->stats.ack_timeouts++;

                if (retransmit > session->timeouts || send_until_answered) {
                    session->timeouts++;
                    send_packet(session->type_sent, session, server);
                }
                else {
                    if (server->failover == 1 && session->server_id != 0 && renew_lease == 1) {
                        session->timeouts = 0;
                        session->server_id = 0;
                        TVZERO(session->time_sent);
                        send_packet(session->type_sent, session, server);
                    }
                    else {
                        server->stats.failed++;
                        total_failed++;
                        free_session(server, session);
                    }
                }
            }
        }
    }

    return(0);
}

inline void free_session(dhcp_server_t *server, dhcp_session_t *session) {
    if (session->xid == 0) {
        fprintf(stderr, "free_session: XID is 0!\n");
        exit(1);
    }

    session->timeouts = 0;
    session->naks = 0;
    session->server_id = 0;
    session->type_sent = 0;
    session->type_received = 0;
    TVZERO(session->time_sent);
    TVZERO(session->time_received);
    session->xid = 0;
    session->session_start = 0;
    session->yiaddr = 0;
    session->giaddr = 0;
    session->ciaddr = 0;
    session->lease_time = 0;
    session->options_length = 0;
    server->active--;
    TAILQ_REMOVE(&server->q_inuse, session, link);
    TAILQ_INSERT_TAIL(&server->q_free, session, link);

    return;
}

int reader(void) {
    int num_read = 0;
    int pollto = 20;
    ssize_t packet_length;
    static uint8_t buffer[1024];
    struct timeval timestamp;
    struct pollfd fds = {sock, POLLIN, 0};

    while (poll(&fds, 1, pollto) > 0) {
#ifdef PCAP
        if (ifname)
            packet_length = receive_pcap(buffer, &timestamp);
        else {
#endif
            packet_length = recv(sock, buffer, sizeof(buffer), 0);
#ifdef __linux__
            ioctl(sock, SIOCGSTAMP, &timestamp);
#else
            gettimeofday(&timestamp, NULL);
#endif
#ifdef PCAP
        }
#endif
        if (packet_length < 0) {
            fprintf(logfp, "Packet receive error\n");
            return(0);
        }

        num_read++;
        pollto = 0;
        process_packet((struct dhcp_packet *) buffer, &timestamp, packet_length);
    }

    if (fds.revents & (POLLERR | POLLNVAL))
        fprintf(stderr, "reader: poll socket error\n");

    return(num_read);
}

int process_packet(struct dhcp_packet *packet, struct timeval *timestamp, uint32_t length) {
    int dhcp_type = -1;
    int found = 0;
    char *fqdn = NULL;
    uint8_t *options = packet->options;
    uint32_t offset = 4;
    uint32_t xid = ntohl(packet->xid);
    uint32_t dt;
    dhcp_server_t *server;
    dhcp_session_t *session = NULL;
    dhcp_stats_t *stats = NULL;
    in_addr_t server_id = 0;
    static double deltat, elapsed;

    for (server = servers; server != NULL; server = server->next) {
        TAILQ_FOREACH(session, &server->q_inuse, link) {
            if (session->xid == xid && memcmp(packet->chaddr, session->mac, 6) == 0) {
                found = 1;
                break;
            }
        }

        if (found == 1)
            break;
    }

    if (server == NULL || session == NULL)
        return(-1);

    /* Find packet type */
    if (memcmp(options, DHCP_OPTIONS_COOKIE, 4) != 0 && bootp == 0) {
        fprintf(stderr, "Bad DHCP magic cookie\n");
        server->stats.errors++;
        server->stats.failed++;
        total_failed++;
        free_session(server,session);
        return(-1);
    }

    while (offset + DHCP_FIXED_NON_UDP < length && options[offset] != DHO_END) {
        if (options[offset] == DHO_DHCP_MESSAGE_TYPE) {
            dhcp_type = options[offset + 2];
            if (dhcp_type == DHCPOFFER)
                options[offset + 2] = DHCPREQUEST;    /* reuse options */
        }
        else if (options[offset] == DHO_FQDN && verbose)
            fqdn = unpack81(options + offset);
        else if (options[offset] == DHO_DHCP_LEASE_TIME)
            session->lease_time = ntohl(*((int *) (options + offset + 2)));
        else if (options[offset] == DHO_DHCP_SERVER_IDENTIFIER && server_id == 0)
            server_id = *((int *) (options + offset + 2));
        else if (options[offset] == DHO_PAD) {
            offset++;
            continue;
        }

        offset += options[offset + 1] + 2;
    }

    if (dhcp_type == -1 && bootp == 0) {
        fprintf(stderr, "DHCP message type not found in packet\n");
        return(-1);
    }

    TVSET(server->last_packet_received, (*timestamp));
    TVSET(session->time_received, (*timestamp));

    if (session->yiaddr == 0)
        session->yiaddr = packet->yiaddr.s_addr;

    if (server->failover && server_id == server->fa.sin_addr.s_addr)
        stats = &server->peer_stats;
    else
        stats = &server->stats;

    if (fqdn != NULL)
        strncpy(session->hostname, fqdn, sizeof(session->hostname));

    if (bootp) {
        stats->offers_received++;
        session->type_received = BOOTP_REPLY;
        server->stats.completed++;
        total_completed++;
        if (outfp != NULL)
            print_lease(outfp, session);
        free_session(server, session);
        return(0);
    }

    session->options_length = offset - 4;
    memcpy(session->options, packet->options + 4, offset - 3);
    dt = DELTATV((*timestamp), session->time_sent);

    switch (dhcp_type) {
        case DHCPOFFER:
            stats->offers_received++;
            session->type_received = DHCPOFFER;
            stats->offer_latency_avg += dt;
            if (dt < stats->offer_latency_min)
                stats->offer_latency_min = dt;
            if (dt > stats->offer_latency_max)
                stats->offer_latency_max = dt;

            if (dhcp_ping == 1) {
                server->stats.completed++;
                total_completed++;
                if (outfp != NULL)
                    print_lease(outfp, session);
                free_session(server, session);
            }
            else {
                session->timeouts = 0;
                send_packet(DHCPREQUEST, session, server);
            }

            break;
        case DHCPACK:
            session->server_id = server_id;
            stats->acks_received++;
            session->type_received = DHCPACK;
            stats->ack_latency_avg += dt;

            if (dt < stats->ack_latency_min)
                stats->ack_latency_min = dt;

            if (dt > stats->ack_latency_max)
                stats->ack_latency_max = dt;

            if (outfp != NULL)
                print_lease(outfp, session);

            if (send_release) //session freed in send_packet
                send_packet(DHCPRELEASE, session, server);
            else {
                server->stats.completed++;
                total_completed++;
                free_session(server, session);
            }

            if (stats_interval != 0 && total_completed % stats_interval == 0) {
                if (server->last_stat.tv_sec == 0)
                    deltat = DELTATVS((*timestamp), server->first_packet_sent);
                else
                    deltat = DELTATVS((*timestamp), server->last_stat);

                elapsed = DELTATVS((*timestamp), server->first_packet_sent);
                fprintf(logfp, "%.2f STATS %-15s %6u leases %6.1f (lps) Failed: %6u\n", elapsed,
                               inet_ntoa(server->sa.sin_addr), total_completed,
                               (double)(total_completed - server->stats.acks_last) / deltat, total_failed);
                server->stats.acks_last = total_completed;
                TVSET(server->last_stat, (*timestamp));
            }
            break;
        case DHCPNAK:
            if (session->type_received == DHCPACK)
                fprintf(logfp, "Received late NAK -- ignoring\n");
            else {
                stats->naks_received++;
                session->naks++;
                session->type_received = DHCPNAK;
            }

            if (server->failover == 1 && session->naks + session->timeouts < retransmit) {
                session->naks++;

                if (verbose)
                    fprintf(logfp, "%d naks received. Retrying %u\n", session->naks, session->xid);

                memset(session->options, '\0', DHCP_MAX_OPTION_LEN);
                TVZERO(session->time_sent);
                session->server_id = 0;
                session->yiaddr = 0;
                send_packet(DHCPDISCOVER, session, server);
            }
            else {
                if (verbose)
                    fprintf(logfp, "%d naks received. Aborting %u\n", session->naks, session->xid);

                server->stats.failed++;
                total_failed++;
                free_session(server, session);
            }
            break;
        case DHCPLEASEUNKNOWN:
        case DHCPLEASEUNASSIGNED:
        case DHCPLEASEACTIVE:
            total_completed++;
            server->stats.completed++;
            free_session(server, session);
            break;
        default:
            fprintf(logfp, "Unknown DHCP type: %d\n", dhcp_type);
            session->type_received = -1;
            return(-1);
    }

    if (verbose)
        print_packet(length, packet);

    return(0);
}

void parse_args(int argc, char **argv) {
    char ch;
    int i;
    uint64_t val;
    int temp[6];

    if (argc < 3)
        usage();

    while ((ch = getopt(argc, argv, "a:bBc:Cd:DeEf:F:G:hHi:I:kl:L:mn:No:O:pP:q:rR:s:t:T:u:vwx:z")) != -1) {
        switch (ch) {
            case 'a':
                if (strchr(optarg, ':') == NULL) {
                    val = atoll(optarg);
                    for (i = 0; i < 6; i++)
                        firstmac[5 - i] = (val & (0x00ffULL << i * 8)) >> i * 8;
                }
                else {
                    if (sscanf(optarg, "%2x:%2x:%2x:%2x:%2x:%2x",
                               temp, temp + 1, temp + 2, temp + 3, temp + 4, temp + 5) < 6) {
                        fprintf(stderr, "\nBad MAC Address in -a option: %s\n", optarg);
                        usage();
                    }

                    for (i = 0; i < 6; i++)
                        firstmac[i] = (char) temp[i];
                }

                use_sequential_mac = 1;
                break;
            case 'b':
                broadcast = 1;
                break;
            case 'B':
                fprintf(stderr, "\nSimulating BOOTP\n");
                bootp = 1;
                break;
            case 'c':
                if (inet_aton(optarg, &srcaddr) == 0) {
                    fprintf(stderr, "Invalid source address %s\n", optarg);
                    exit(1);
                }
                break;
            case 'C':
                send_opt50 = 1;
                break;
            case 'd':
                target_rate = atof(optarg);
                break;
            case 'D':
                no_opt_req = 1;
                break;
            case 'e':
                random_mac = 1;
                break;
            case 'E':
                renew_both_peers = 1;
                break;
            case 'f':
                input_file = strdup(optarg);
                break;
            case 'F':
                send_opt81 = 1;
                if (parse81(optarg) < 0)
                    usage();
                break;
            case 'G':
                send_inform = 1;

                if (addoption(DHO_DHCP_PARAMETER_REQUEST_LIST, optarg, &extraoptions) == NULL)
                    usage();
                break;
            case 'h':
                send_hostname = 1;
                break;
            case 'H':
                random_hostname = 1;
                send_hostname = 1;
                break;
            case 'i':
                if (add_servers(optarg) < 0)
                    exit(1);
                break;
            case 'I':
#ifdef PCAP
                ifname = strdup(optarg);
                if (!parse)
                    fprintf(logfp, "PCAP/DNET on interface: %s\n", ifname);
#else
                fprintf(logfp, "Not compiled with PCAP/DNET support");
                usage();
#endif
                break;
            case 'k':
                parse = 1;
                logfp = stdout;
                break;
            case 'l':
                logfile = strdup(optarg);
                break;
            case 'L':
                test_length = atol(optarg);
                break;
            case 'm':
                use_sequential_mac = 1;
                break;
            case 'n':
                number_requests = atol(optarg);
                break;
            case 'N':
                send_until_answered = 1;
                break;
            case 'o':
                output_file = strdup(optarg);
                break;
            case 'O':
                {
                    int option;
                    char *s;

                    option = strtol(optarg, &s, 0);
                    if (option == 0xff || s[0] != ':' || s[1] == '\0')
                        usage();

                    if (addoption(option, s + 1, &extraoptions) == NULL)
                        usage();
                }
                break;
            case 'p':
                dhcp_ping = 1;
                break;
            case 'P':
                server_port = atol(optarg);
                break;
            case 'q':
                max_sessions = atol(optarg);
                break;
            case 'r':
                send_release = 1;
                break;
            case 'R':
                retransmit = atol(optarg);
                break;
            case 's':
                stats_interval = atol(optarg);
                break;
            case 't':
                timeout = atof(optarg) / 1000.;
                break;
            case 'T':
                secs_offset = atol(optarg);
                break;
            case 'u':
                send_opt61 = 1;
                if (optarg == NULL || strncmp(optarg, "MAC", 3) == 0) {
                    fprintf(stderr, "MAC will be used for option61\n");
                }
                else {
                    if (strncmp(optarg, "0x", 2) != 0) {
                        opt61_string = strdup(optarg);
                        opt61_strlen = strlen(opt61_string);
                    }
                    else {
                        int x;
                        int i;

                        opt61_strlen = strlen(optarg + 2) / 2;
                        if ((opt61_string = malloc(opt61_strlen)) == NULL) {
                            fprintf(stderr, "\n\tMalloc failed!\n");
                            exit(66);
                        }

                        for (i = 0; i < opt61_strlen; i++) {
                            sscanf(optarg + 2 + 2 * i, "%2x", &x);
                            opt61_string[i] = x;
                        }
                    }
                }
                break;
            case 'v':
                verbose += 1;
                break;
            case 'w':
                renew_lease = 1;
                break;
            case 'x':
                if (parse82(optarg) < 0)
                    usage();
                break;
            case 'z':
                hwlen_zero = 1;
                fprintf(stderr, "Setting chlen to zero\n");
                break;
            case '?':
            default:
                usage();
        }
    }

    if (servers == NULL) {
        fprintf(stderr, "No servers defined\n");
        usage();
    }
}

int add_servers(const char *s) {
    const char *p1 = s;
    char buffer[16];
    int len, failover = 0;
    dhcp_server_t *sp = NULL;

    assert(s != NULL);

    while (*p1 != '\0') {
        while (*p1 != ',' && *p1 != '\0' && *p1 != ':')
            p1++;

        len = p1 - s;
        if (len == 0 || len + 1 > sizeof(buffer))
            return(-1);

        strncpy(buffer, s, len);
        s = p1 + 1;
        buffer[len] = '\0';

        if (failover) {
            assert(sp);
            sp->peer_stats.offer_latency_min = 10000000;
            sp->peer_stats.ack_latency_min = 10000000;
            sp->fa.sin_port = htons(server_port);
            sp->fa.sin_family = AF_INET;
            if (inet_aton(buffer, &sp->fa.sin_addr) == 0) {
                fprintf(stderr, "Invalid address %s\n", buffer);
                return(-1);
            }

            failover = 0;
            sp->failover = 1;
            if (*p1 != '\0')
                p1++;

            continue;
        }

        if (*p1 == ':')
            failover++;

        if (*p1 != '\0')
            p1++;

        sp = malloc(sizeof(dhcp_server_t));
        assert(sp);

        memset(sp, '\0', sizeof(dhcp_server_t));
        sp->stats.offer_latency_min = 10000000;
        sp->stats.ack_latency_min = 10000000;
        sp->sa.sin_port = htons(server_port);
        sp->sa.sin_family = AF_INET;

        if (inet_aton(buffer, &sp->sa.sin_addr) == 0) {
            fprintf(stderr, "Invalid address %s\n", buffer);
            return(-1);
        }

        sp->next = servers;
        servers = sp;
        num_servers++;
    }

    return(0);
}

int pack61(uint8_t *options, dhcp_session_t *session) {
    options[0] = DHO_DHCP_CLIENT_IDENTIFIER;

    if (opt61_strlen == 0) {
        options[1] = 7;
        options[2] = 0;
        memcpy(options + 3, session->mac, 6);

        return(9);
    }

    options[1] = opt61_strlen;
    memcpy(options + 2, opt61_string, opt61_strlen);

    return(opt61_strlen + 2);
}

int pack82(uint8_t *options, dhcp_session_t *session) {
    int offset = 0;
    int opt82_length = 0;
    int subopt_length = 0;

    if (opt82_subopts == NULL)
        return(0);

    // Start with Option Code 82
    options[offset] = DHO_DHCP_AGENT_OPTIONS;
    // Skip both the code and the length fields.  We'll fill in
    // the length field when we're done building the whole option.
    offset += 2;

    if (opt82_subopts->send_circuit_id) {
        options[offset] = RAI_CIRCUIT_ID;
        offset++;

        if (opt82_subopts->circuit_id) {
            subopt_length = strlen(opt82_subopts->circuit_id);
            memcpy(options + offset + 1, opt82_subopts->circuit_id, subopt_length);
        } else {
            subopt_length = sprintf((char *)options + offset + 1,
                                    "%02x___%02x___%02x___%02x___%02x___%02x",
                                    session->mac[0], session->mac[1], session->mac[2],
                                    session->mac[3], session->mac[4], session->mac[5]);
        }

        options[offset] = subopt_length;
        offset += subopt_length + 1;
        opt82_length += subopt_length + 2;
    }

    if (opt82_subopts->send_remote_id) {
        options[offset] = RAI_REMOTE_ID;
        offset++;

        if (opt82_subopts->remote_id) {
            subopt_length = strlen(opt82_subopts->remote_id);
            memcpy(options + offset + 1, opt82_subopts->remote_id, subopt_length);
        } else {
            subopt_length = sprintf((char *)options + offset + 1,
                                    "%02x___%02x___%02x___%02x___%02x___%02x",
                                    session->mac[0], session->mac[1], session->mac[2],
                                    session->mac[3], session->mac[4], session->mac[5]);
        }

        options[offset] = subopt_length;
        offset += subopt_length + 1;
        opt82_length += subopt_length + 2;
    }

    if (opt82_subopts->link_selection.s_addr != INADDR_ANY) {
        options[offset] = RAI_LINK_SELECT;
        options[offset + 1] = 4; // sizeof (struct in_addr)
        memcpy(options + offset + 2 , &opt82_subopts->link_selection, 4);
        offset += 6;
        opt82_length += 6;
    }

    if (opt82_subopts->server_id_override.s_addr != INADDR_ANY) {
        options[offset] = RAI_SERVER_ID_OVERRIDE;
        options[offset + 1] = 4; // sizeof (struct in_addr)
        memcpy(options + offset + 2, &opt82_subopts->server_id_override, 4);
        offset += 6;
        opt82_length += 6;
    }

    // Now that we know total option 82 length
    // we can set it in the options buffer
    options[1] = opt82_length;

    // Return the entire option length including the option code and option length
    return(opt82_length + 2);
}

int pack81(uint8_t *options, const char *hostname) {
    char *bp, *cp, *plen;
    int hnlen;
    int length = 0;

    assert(hostname);
    assert(domain81);

    hnlen = strlen(hostname);

    options[0] = DHO_FQDN;
    options[2] = flags81;
    options[3] = 0;
    options[4] = 0;

    if (!(flags81 & EOPT81)) {
        memcpy(options + 5, hostname, hnlen);
        memcpy(options + 5 + hnlen, domain81, domain81_len);
        options[1] = 3 + hnlen + domain81_len;
        return(options[1] + 2);
    }

    options[5] = hnlen;
    memcpy(options + 6, hostname, hnlen);
    plen = (char *) options + 6 + hnlen;
    *plen = 0;
    length = 5 + hnlen;
    cp = domain81 + 1;
    bp = plen + 1;
    while (*cp != '\0') {
        if (*cp == '.') {
            plen = bp++;
            *plen = 0;
            length++;
            cp++;
            continue;
        }

        (*plen)++;
        *bp++ = *cp++;
        length++;
    }

    *bp = '\0';
    options[1] = length + 1;

    return(length + 3);
}

int parse81(char *s) {
    char *p1 = s;
    char buf[128];
    int len;

    while (*p1 != '\0' && *p1 != ':')
        p1++;

    len = p1 - s;
    if (len > sizeof(buf) - 1)
        len = sizeof(buf) - 1;

    *buf = '.';
    strncpy(buf + 1, s, len);
    buf[len + 1] = '\0';
    domain81 = strdup(buf);
    domain81_len = strlen(domain81);

    if (*p1 == '\0')
        return(0);

    while (*p1) {
        switch (*p1) {
            case 'S':
            case 's':
                flags81 |= SOPT81;
                break;
            case 'O':
            case 'o':
                flags81 |= OOPT81;
                break;
            case 'E':
            case 'e':
                flags81 |= EOPT81;
                break;
            case 'N':
            case 'n':
                flags81 |= NOPT81;
                break;
        }

        p1++;
    }

    fprintf(stderr, "Option 81 Enabled:\n\t Domain: %s Length %u\n", domain81, domain81_len);

    if (flags81 & SOPT81)
        fputs("\t\tS bit set\n", logfp);

    if (flags81 & OOPT81)
        fputs("\t\tO bit set\n", logfp);

    if (flags81 & EOPT81)
        fputs("\t\tE bit set\n", logfp);

    if (flags81 & NOPT81)
        fputs("\t\tN bit set\n", logfp);

    fputs("", logfp);

    return(1);
}

int parse82(char *s) {
    char *subopts;
    char *value;
    char *p;
    char subopt;

    if ((s == NULL) || (*s == '\0')) {
        fprintf(stderr, "Option 82 requires sub-options\n");
        usage();
        exit(1);
    }

    opt82_subopts = malloc(sizeof(ra_subopts_t));
    memset(opt82_subopts, 0, sizeof(ra_subopts_t));

    subopts = strdup(s);

    p = subopts;
    while (*p != '\0') {
        while (isspace(*p))
            p++;

        subopt = *p;
        p++;
        value = p;

        if ((subopt != 'r') && (subopt != 'c') &&
            (subopt != 'l') && (subopt != 's')) {
            fprintf(stderr, "Unsupported Option 82 sub-option %c\n", subopt);
            usage();
            exit(1);
        }

        while (*p != ',' && *p != '\0')
            p++;

        if (*p == ',') {
            *p = '\0';
            p++;
        }

        value = strchr(value, '=');
        if ((value == NULL) && (subopt != 'r') && (subopt != 'c')) {
            fprintf(stderr, "Option 82 sub-option %c must have a value\n", subopt);
            usage();
            exit(1);
        } else if (value != NULL) {
            value++;
            while (isspace(*value))
                value++;
        }

        switch (subopt) {
            case 'r':
                opt82_subopts->send_remote_id = 1;
                if (value != NULL) {
                    opt82_subopts->remote_id = value;
                }

                break;

            case 'c':
                opt82_subopts->send_circuit_id = 1;
                if (value != NULL) {
                    opt82_subopts->circuit_id = value;
                }

                break;

            case 'l':
                if (inet_aton(value, &(opt82_subopts->link_selection)) == 0) {
                    fprintf(stderr, "Invalid link-selection address: %s\n", value);
                    usage();
                    exit(1);
                }
                break;

            case 's':
                if (inet_aton(value, &(opt82_subopts->server_id_override)) == 0) {
                    fprintf(stderr, "Invalid server-id-override address: %s\n", value);
                    usage();
                    exit(1);
                }
                break;

            default:
                // We should never get here
                fprintf(stderr, "Unsupported Option 82 sub-option %c\n", subopt);
                exit(1);
                break;
        }
    }

    return(1);
}

char *unpack81(uint8_t *options) {
    int length = options[1];
    static char buf[256];
    char *cp, *len, *bp;

    assert(options);
    fprintf(stderr, "Option 81 length: %u S%u/O%u/E%u/N%u\n", length, (options[2] & SOPT81),
                    (options[2] & OOPT81) >> 1, (options[2] & EOPT81) >> 2, (options[2] & NOPT81) >> 3);
    fprintf(stderr, " A-RCODE: %u PTR-RCODE: %u\n", options[3], options[4]);

    if (!(options[2] & EOPT81)) {
        memcpy(buf, options + 5, length - 3);
        buf[length - 3] = '\0';
    }
    else {
        len = (char *) options + 5;
        cp = (char *) options + 6;
        bp = buf;
        length -= 5;

        if (length > sizeof(buf) - 2) {  /* FixME Not correct */
            fprintf(logfp, "opt81: FQDN too large %u\n", length);
            return(NULL);
        }

        while (length > 0 && *cp != '\0' && *cp != '.') {
            memcpy(bp, cp, *len);
            bp += *len;
            *bp++ = '.';
            length -= *len + 1;
            len += *len + 1;
            cp = len + 1;
        }

        *bp++ = '\0';
    }

    if (*buf)
        fprintf(stderr, " FQDN: %s\n", buf);

    return(buf);
}

void usage() {
//TODO: Add missing parameters
    fprintf(stderr,
            "\nUsage: dras -i <DHCP server IP> -c <relay agent IP> -n <number requests> \n"
            "  [-q <max outstanding>] [ -d delay] [-f <input-lease-file>] [-l <logfile>]\n"
            "  [-o <output-lease-file>] [-F <domain>:S|O|E|N] [-t <timeout> ]\n"
            "  [-a <starting-mac-address>] [-P dest-port] [-s interval ]\n"
            "  [-O <dec option-no>:<hex data>] [-b|B|g|h|k|m|N|r|p|R|s|u|w]\n\n"
            "  -a Starting MAC address (implies -m) (default 00:00:00:00:00:00).\n"
            "  -b Use broadcast (-i is ignored)\n"
            "  -B Send BOOTP requests, expect BOOTP replies\n"
            "  -c DHCP Relay Agent IP address\n"
            "  -C Send option 50 instead of client ip address\n"
            "  -d Maximum rate of new transactions\n"
            "  -D Disable sending parameter request list, option 55 data\n"
            "  -e Replace MACs in lease file with random values\n"
            "  -E Send renew to both FO peers and set broadcast flag\n"
            "  -f Input file with MAC/IP/hostname leases\n"
            "  -F Send opt81 FQDN:[S|O|E|N]\n"
            "  -G Send INFORM request with options as hex\n"
            "  -h Send DHCP option 12, hostname (Derived from the MAC address).\n"
            "  -H Send random option 12 hostname (Implies -h).\n"
            "  -i DHCP Server IP Address (multiple servers separated by commas)\n"
            "          Failover peers separated by ':'s\n");
    fprintf(stderr,
#ifdef PCAP
            "  -I Ethernet interface for PCAP listener (enable PCAP/DNET)\n"
#endif
            "  -k write output in parsable format to stdout\n"
            "  -l output logfile (default: stderr)\n"
            "  -L Test length in seconds.\n"
            "  -m Use sequential MAC (Default random)\n"
            "  -n DHCP Number of requests\n"
            "  -N Retransmit until answer received\n"
            "  -o Output lease file \n"
            "  -O Send option <option-no> (dec) with data <hex data> (w/o length)\n"
            "  -p ping mode.  End after DHCPOFFER received.\n"
            "  -P DHCP server port (default 67)\n"
            "  -q Maximum outstanding requests\n"
            "  -r Send RELEASE after ACK received\n"
            "  -R Number of retransmits (default 0)\n"
            "  -s Print performance every N leases\n"
            "  -t Timeout on requests (ms)\n"
            "  -T Number of seconds to add to the packet's secs field\n"
            "  -u Send option 61 (UUID)\n"
            "  -v Verbose output\n"
            "  -w Send ciaddr in request packet (renew mode)\n"
            "  -x Send option 82 and suboption(s) r|c|l|s\n"
            "       Mulitple sub-options separated by commas\n"
            "       r[=Remote ID], c[=Circuit ID], l=Link Selection, s=Server ID Override\n"
            "  -z Set client hardware address length to zero\n");

    exit(1);
}

void getmac(uint8_t * s) {
    int carry = 5;
    int i1, i2;

    if (use_sequential_mac) {
        if (s)
            memcpy(s, firstmac, 6);

        while (carry >= 0) {
            if (firstmac[carry] == 0xFF)
                firstmac[carry--] = 0;
            else {
                firstmac[carry]++;
                return;
            }
        }

        return;
    }

    if (s) {
        i1 = rand();
        i2 = rand();

        memcpy(s, &i1, 4);
        memcpy(s + 4, &i2, 2);
    }
}

void print_packet(size_t len, struct dhcp_packet *p) {
    int i, offset = 4;
    uint32_t dhcp_type;
    uint32_t x;
    uint8_t *options = (uint8_t *) p->options;
    static char ipbuf[16];
    static char *typestrings[] = {"DHCPDISCOVER", "DHCPOFFER", "DHCPREQUEST", "DHCPDECLINE",
                                  "DHCPACK", "DHCPNAK", "DHCPRELEASE", "DHCPINFORM"};

    fprintf(logfp, "------ XID %u ------\nlength %u op = %d  htype = %d  hlen = %d"
                   "  hops = %d secs = %u flags = %x\n",
                   ntohl(p->xid), (unsigned)len, p->op, p->htype, p->hlen, p->hops, ntohs(p->secs),
                   p->flags);

    fprintf(logfp, "ciaddr = %s\n", inet_ntoa(p->ciaddr));
    fprintf(logfp, "yiaddr = %s\n", inet_ntoa(p->yiaddr));
    fprintf(logfp, "siaddr = %s\n", inet_ntoa(p->siaddr));
    fprintf(logfp, "giaddr = %s\n", inet_ntoa(p->giaddr));
    fprintf(logfp, "chaddr = %2.2x:%2.2x:%2.2x:%2.2x:%2.2x:%2.2x\n",
                   ((unsigned char *) (p->chaddr))[0], ((unsigned char *) (p->chaddr))[1],
                   ((unsigned char *) (p->chaddr))[2], ((unsigned char *) (p->chaddr))[3],
                   ((unsigned char *) (p->chaddr))[4], ((unsigned char *) (p->chaddr))[5]);

    *(p->file + DHCP_FILE_LEN - 1) = '\0';
    *(p->sname + DHCP_SNAME_LEN - 1) = '\0';

    while (offset + DHCP_FIXED_NON_UDP < len && options[offset] != DHO_END) {
        if (options[offset] == DHO_DHCP_MESSAGE_TYPE) {
            dhcp_type = options[offset + 2];
            if (dhcp_type < 9 && dhcp_type > 0)
                fprintf(logfp, "Packet Type %u: %s\n", dhcp_type, typestrings[dhcp_type - 1]);

            /* We set OFFER to REQUEST to reuse packet in process_packet */
            if (dhcp_type == 3)
                dhcp_type = 2;
        }
        else if (options[offset] == DHO_FQDN)
            unpack81(options + offset);
        else if (options[offset] == DHO_DHCP_LEASE_TIME) {
            x = *((int *) (options + offset + 2));
            fprintf(logfp, "Lease Time: %u\n", ntohl(x));
        }
        else if (options[offset] == DHO_DHCP_RENEWAL_TIME) {
            x = *((int *) (options + offset + 2));
            fprintf(logfp, "Renewal Time: %u\n", ntohl(x));
        }
        else if (options[offset] == DHO_DHCP_REBINDING_TIME) {
            x = *((int *) (options + offset + 2));
            fprintf(logfp, "Rebinding Time: %u\n", ntohl(x));
        }
        else if (options[offset] == DHO_DHCP_SERVER_IDENTIFIER) {
            x = *((int *) (options + offset + 2));
            fprintf(logfp, "DHCP Server ID: %s\n", addrtoa(x, ipbuf));
        }
        else if (options[offset] == DHO_PAD) {
            offset++;
            continue;
        }
        else {
            fprintf(logfp, "Option %3d: Length %3d Data: 0x", options[offset], options[offset + 1]);

            if (options[offset + 1] > 0)
                for (i = 0; i < options[offset + 1]; i++)
                    fprintf(logfp, "%02X", options[offset + 2 + i]);

            fprintf(logfp, "\n");
        }

        offset += options[offset + 1] + 2;
    }
}

/* Caller, make sure the buf points to a char [16] or larger */
inline char *addrtoa(uint32_t addr, char *buf) {
    uint32_t n = ntohl(addr);
    *buf = '.';
    snprintf(buf, 16, "%u.%u.%u.%u", (n & 0xff000000) >> 24,
             (n & 0x00ff0000) >> 16, (n & 0x0000ff00) >> 8, (n & 0x000000ff));

    return(buf);
}

int read_lease_data(lease_data_t **leases) {
    char buf[1024], hostname[64], ipstr[16];
    int ret, i, read_count = 0;
    in_addr_t ipaddr;
    uint8_t mac[6];
    lease_data_t *lease = *leases;
    FILE *fpin;
    int temp[6];
    char *tokes[MAX_TOKENS];
    char *s;
    int ntokes;
    int lineno = 0;
    int option_no;
    DHCP_OPTION *tail = NULL;

    fpin = fopen(input_file, "r");
    if (fpin == NULL) {
        fprintf(logfp, "Could not open input file: %s\n", input_file);
        return(0);
    }

    while (fgets(buf, sizeof(buf), fpin) != NULL) {
        lineno++;

        if ((ntokes = get_tokens(buf, tokes, MAX_TOKENS)) < 2) {
            fprintf(logfp, "Too few tokens: %d, line %d\n", ntokes, lineno);
            continue;
        }

        *ipstr = '\0';
        *hostname = '\0';
        ret = sscanf(tokes[0], "%2x:%2x:%2x:%2x:%2x:%2x", temp, temp + 1, temp + 2, temp + 3, temp + 4, temp + 5);
        if (ret < 6) {
            fprintf(logfp, "Line %d, MAC format error: %s\n", lineno, tokes[0]);
            continue;
        }

        for (i = 0; i < 6; i++)
            mac[i] = (char) temp[i];

        if (*tokes[1] == '\0' || (ipaddr = inet_addr(tokes[1])) == INADDR_NONE) {
            if (strncmp(tokes[1], "DISC", 4) == 0)
                ipaddr = 0;
            else {
                fprintf(logfp, "Line %d, format error: %s\n", lineno, tokes[1]);
                continue;
            }
        }

        if (*leases == NULL) {
            *leases = calloc(1, sizeof(lease_data_t));
            lease = *leases;
        }
        else {
            lease->next = calloc(1, sizeof(lease_data_t));
            lease = lease->next;
        }

        assert(lease != NULL);
        lease->ipaddr = ipaddr;
        memcpy(lease->mac, mac, 6);
        lease->next = NULL;

        if (lease->ipaddr == 0)
            lease->start_from = DHCPDISCOVER;
        else
            lease->start_from = DHCPREQUEST;

        if (ntokes > 2 && *tokes[2] != '-')
            lease->hostname = strdup(tokes[2]);
        else
            lease->hostname = NULL;

        if (ntokes > 3 && (ipaddr = inet_addr(tokes[3])) != INADDR_NONE)
            lease->server_id = ipaddr;

        lease->giaddr = srcaddr.s_addr;
        read_count++;

        if (ntokes < 5)
            continue;

        tail = NULL;

        for (i = 4; i < ntokes; i++) {
            if (strncasecmp(tokes[i], "GIADDR:", 7) == 0) {
                if (inet_aton(tokes[i] + 7, (struct in_addr *) &lease->giaddr) == 0)
                    fprintf(stderr, "Invalid lease giaddr %s\n", tokes[i]);

                continue;
            }
            else if (strncasecmp(tokes[i], "CTIME:", 6) == 0)
                continue;
            else if (strncasecmp(tokes[i], "START:", 6) == 0) {
                if (lease->ipaddr == 0) {
                    fprintf(stderr, "No IP addr for this lease. Must Discover\n");
                    continue;
                }

                if (strncasecmp(tokes[i] + 6, "RELEASE", 7) == 0)
                    lease->start_from = DHCPRELEASE;
                else if (strncasecmp(tokes[i] + 6, "INFORM", 6) == 0)
                    lease->start_from = DHCPINFORM;
                else if (strncasecmp(tokes[i] + 6, "RENEW", 5) == 0)
                    lease->start_from = DHCPREQUEST;
                else if (strncasecmp(tokes[i] + 6, "QUERY", 5) == 0)
                    lease->start_from = DHCPLEASEQUERY;
            }
            else if (strncasecmp(tokes[i], "OPT:", 4) == 0) {
                option_no = strtol(tokes[i] + 4, &s, 0);

                if (option_no == 0xff || s[0] != ':' || s[1] == '\0') {
                    fprintf(stderr, "Bad option: %s\n", tokes[i]);
                    continue;
                }

                if ((tail = addoption(option_no, s + 1, &lease->options)) == NULL) {
                    fprintf(stderr, "Bad option: %s\n", tokes[i]);
                    continue;
                }
            }
            else
                fprintf(stderr, "read_leases: What is %s?\n", tokes[i]);
        }

        if (extraoptions) {
            if (tail)
                tail->next = extraoptions;
            else
                lease->options = extraoptions;
        }
    }

    return(read_count);
}

DHCP_OPTION *addoption(int option_no, char *hexdata, DHCP_OPTION **list) {
    int i;
    int datalen = strlen(hexdata);
    char *data;
    int is_string;
    DHCP_OPTION *popt;

    for (popt = *list; popt && popt->next; popt = popt->next);

    if (*hexdata == 'S' || *hexdata == 's') {
        is_string = 1;
        datalen--;
        hexdata++;
    }
    else {
        is_string = 0;
        if (datalen % 2 != 0) {
            fprintf(stderr, "Odd number of hex chars\n");
            return(NULL);
        }

        datalen /= 2;
        if (strspn(hexdata, "0123456789abcdefABCDEF") != datalen * 2 || datalen > 255) {
            fprintf(stderr, "Illegal hex chars or too long (max 255)\n");
            return(NULL);
        }
    }

    if (popt) {
        popt->next = calloc(1, sizeof(DHCP_OPTION));
        popt = popt->next;
    }
    else {
        popt = calloc(1, sizeof(DHCP_OPTION));
        *list = popt;
    }

    data = malloc(datalen);
    popt->data = data;

    popt->option_no = option_no;
    popt->data_len = datalen;
    popt->discover_only = 0;

    if (is_string) {
        memcpy(popt->data, hexdata, datalen);
    }
    else {
        for (i = 0; hexdata[i]; i += 2) {
            int x;

            sscanf(hexdata + i, "%2x", &x);
            *data++ = (char) (x & 0377);
        }
    }

    return(popt);
}

uint32_t get_local_addr(void) {
    int sock;
    struct sockaddr_in ca;
    socklen_t calen = sizeof(ca);

    if (servers == NULL) {
        fprintf(logfp, "get_local_addr: servers list is NULL\n");
        exit(1);
    }

    if ((sock = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
        perror("socket:");
        exit(1);
    }

    if (connect(sock, (const struct sockaddr *)&servers->sa, sizeof(servers->sa)) < 0) {
        perror("get_local_addr: Connect");
        return(INADDR_ANY);
    }

    getsockname(sock, (struct sockaddr *)&ca, &calen);
    close(sock);

    return(ca.sin_addr.s_addr);
}

int get_tokens(char *cp, char **tokes, int maxtokes) {
    int n = 0;

    if (cp == NULL)
        return(0);

    /* Eat any leading whitespace */
    while (*cp == ' ' && cp != '\0')
        cp++;

    if (*cp == '\0')
        return(0);

    tokes[0] = cp;
    while (*cp != '\0' && *cp != '\n') {
        if (*cp == ' ' || *cp == '\t') {
            *(cp++) = '\0';

            while (*cp != '\0' && (*cp == ' ' || *cp == '\t'))
                cp++;

            if (++n < maxtokes)
                tokes[n] = cp;
            else
                return(0);
        }
        else
            cp++;
    }

    *cp = '\0';

    return(n + 1);
}

void print_lease( FILE *fp, dhcp_session_t *session) {
    static char syiaddr[16], sserver_id[16], sgiaddr[16];
    DHCP_OPTION *popt;
    int i;

    addrtoa(session->yiaddr, syiaddr);
    addrtoa(session->server_id, sserver_id);
    addrtoa(session->giaddr, sgiaddr);
    fprintf(outfp, "%02x:%02x:%02x:%02x:%02x:%02x %-15s %s %-15s GIADDR:%s OPT:51:%08X CTIME:%lu",
            session->mac[0], session->mac[1], session->mac[2], session->mac[3],
            session->mac[4], session->mac[5], syiaddr, session->hostname[0] ? session->hostname : "-",
            sserver_id, sgiaddr, session->lease_time, time(NULL));

    if (session->extra_options) {
        for (popt = session->extra_options; popt; popt = popt->next) {
            fprintf(outfp, " OPT:%u:", popt->option_no);
            for (i = 0; i < popt->data_len; i++)
                fprintf(outfp, "%02X", popt->data[i]);
        }
    }

    fprintf(outfp, "\n");
}
