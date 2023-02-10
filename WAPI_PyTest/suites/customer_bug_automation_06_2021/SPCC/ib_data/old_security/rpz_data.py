import ib_utils.ib_NIOS as ib_NIOS
import json
passthru_obj = {"canonical": "passdn.com", "rp_zone": "rpz.com", "name": "passdn.com.rpz.com"}
passthru_rule=ib_NIOS.wapi_request('POST', object_type="record:rpz:cname", fields=json.dumps(passthru_obj))

    #    logger.info("Add Block Domain Name (No Such Domain) Rule")
no_such_domain_obj = {"canonical": "", "rp_zone": "rpz.com", "name": "blocdnnd.com.rpz.com"}
no_such_domain_rule=ib_NIOS.wapi_request('POST', object_type="record:rpz:cname", fields=json.dumps(no_such_domain_obj))

    #    logger.info("Add Block Domain Name (No Data) Rule")
no_data_obj = {"canonical": "*", "rp_zone": "rpz.com", "name": "blockdn.com.rpz.com"}
no_data_rule=ib_NIOS.wapi_request('POST', object_type="record:rpz:cname", fields=json.dumps(no_data_obj))

    #    logger.info("Add Substitute Domain Name (Domain Name) Rule")
substitute_obj = {"canonical": "google.com", "rp_zone": "rpz.com", "name": "g.com.rpz.com"}
substitute_rule=ib_NIOS.wapi_request('POST', object_type="record:rpz:cname", fields=json.dumps(substitute_obj))

    #    logger.info("Add Substitue (A Record) Rule")
sub_a_rec_obj = {"name":"asm.rpz.com","rp_zone":"rpz.com","ipv4addr":"12.12.12.12"}
sub_a_rec_rule=ib_NIOS.wapi_request('POST', object_type="record:rpz:a", fields=json.dumps(sub_a_rec_obj))

