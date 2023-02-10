package com.cisco.pxgrid.samples.ise;

import java.util.Iterator;
import java.util.List;

import com.cisco.pxgrid.GridConnection;
import com.cisco.pxgrid.model.ise.metadata.SecurityGroup;
import com.cisco.pxgrid.stub.isemetadata.TrustSecClientStub;
import com.cisco.pxgrid.stub.isemetadata.TrustSecQuery;

public class TrustSecMetaDataQuery {
	public static void main(String[] args) throws Exception {
		SampleHelper helper = new SampleHelper();
		GridConnection grid = helper.connectWithReconnectionManager();

		TrustSecClientStub stub = new TrustSecClientStub(grid);
		TrustSecQuery query = stub.createTrustSecQuery();

		List<SecurityGroup> sgps = query.getSecurityGroupList();
		if (sgps != null) {
			SecurityGroup sg;
			for (Iterator<SecurityGroup> it = sgps.iterator(); it.hasNext();) {
				sg = it.next();
				System.out.println("SecurityGroup : id=" + sg.getId()
						+ ", name=" + sg.getName() + ", desc="
						+ sg.getDescription() + ", tag=" + sg.getTag());
			}
		}

		helper.disconnect();
	}
}