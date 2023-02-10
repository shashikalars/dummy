import json
#import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.ib_NIOS_6478 as ib_NIOS
passthru_obj = {"canonical": "passdn.com", "rp_zone": "rpz_feed.com", "name": "passdn.com.rpz_feed.com"}
passthru_rule=ib_NIOS.wapi_request_2('POST', object_type="record:rpz:cname", fields=json.dumps(passthru_obj))

    #    logger.info("Add Block Domain Name (No Such Domain) Rule")
no_such_domain_obj = {"canonical": "", "rp_zone": "rpz_feed.com", "name": "blocdnnd.com.rpz_feed.com"}
no_such_domain_rule=ib_NIOS.wapi_request_2('POST', object_type="record:rpz:cname", fields=json.dumps(no_such_domain_obj))

    #    logger.info("Add Block Domain Name (No Data) Rule")
no_data_obj = {"canonical": "*", "rp_zone": "rpz_feed.com", "name": "blockdn.com.rpz_feed.com"}
no_data_rule=ib_NIOS.wapi_request_2('POST', object_type="record:rpz:cname", fields=json.dumps(no_data_obj))

    #    logger.info("Add Substitute Domain Name (Domain Name) Rule")
substitute_obj = {"canonical": "google.com", "rp_zone": "rpz_feed.com", "name": "g.com.rpz_feed.com"}
substitute_rule=ib_NIOS.wapi_request_2('POST', object_type="record:rpz:cname", fields=json.dumps(substitute_obj))

    #    logger.info("Add Substitue (A Record) Rule")
sub_a_rec_obj = {"name":"asm.rpz_feed.com","rp_zone":"rpz_feed.com","ipv4addr":"12.12.12.12"}
sub_a_rec_rule=ib_NIOS.wapi_request_2('POST', object_type="record:rpz:a", fields=json.dumps(sub_a_rec_obj))
sub_aaaa_rec_obj = {"name":"asm1.rpz_feed.com","rp_zone":"rpz_feed.com","ipv4addr":"22.22.22.22"}
sub_aaaa_rec_rule=ib_NIOS.wapi_request_2('POST', object_type="record:rpz:a", fields=json.dumps(sub_aaaa_rec_obj))
