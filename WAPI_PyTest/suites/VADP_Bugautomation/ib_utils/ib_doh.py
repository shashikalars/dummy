import dns.message
import base64
import os

#############################################################################
#                                                                           #
#   This script is used to perform a DoH query via GET request              #
#   usages: doh_query(<server_IP>,<domain-name>,<RR>, <edns True/False>)    #
#                                                                           #
#############################################################################

def doh_query(ip,domain='infoblox.com',rr='A',edns=True):
    endpoint = "https://"+ip+"/dns-query"    # Converting the DNS server IP to DoH Server format as per the RFC
    message = dns.message.make_query(domain, rr, use_edns=edns)  # Making the DNS query from the domain, RR, edns values
    dns_req = base64.urlsafe_b64encode(message.to_wire()).decode("UTF8").rstrip('=')  #Encoding the DNS query to URLsafe base64 format as per the RFC
    query = "curl -H 'content-type: application/dns-message' "+endpoint+"?dns="+dns_req+" -o - -s -k1 > doh_http2.txt"   # making the DoH GET query
    try:
        op = os.popen(query)
        h = op.read()
        fi = open("doh_http2.txt", "rb").read()
        response = dns.message.from_wire(fi)
        response = response.to_text().encode("utf-8")
        os.remove("doh_http2.txt")
    except:
        print("\nThere is some problem with the DOH server...!!")
        response = "NIL"
    return response
   
