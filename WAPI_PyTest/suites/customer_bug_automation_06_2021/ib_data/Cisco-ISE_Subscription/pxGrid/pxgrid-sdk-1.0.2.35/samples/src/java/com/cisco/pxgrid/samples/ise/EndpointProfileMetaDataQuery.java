package com.cisco.pxgrid.samples.ise;

import java.util.Iterator;
import java.util.List;

import com.cisco.pxgrid.GridConnection;
import com.cisco.pxgrid.model.ise.metadata.EndpointProfile;
import com.cisco.pxgrid.stub.isemetadata.EndpointProfileClientStub;
import com.cisco.pxgrid.stub.isemetadata.EndpointProfileQuery;

public class EndpointProfileMetaDataQuery {
	public static void main(String[] args) throws Exception	{
		SampleHelper helper = new SampleHelper();
		GridConnection grid = helper.connectWithReconnectionManager();

		EndpointProfileClientStub stub = new EndpointProfileClientStub(grid);
		EndpointProfileQuery query = stub.createEndpointProfileQuery();

		List<EndpointProfile> dps = query.getEndpointProfiles();
		if (dps != null) {
			EndpointProfile dp;
			for (Iterator<EndpointProfile> it = dps.iterator(); it.hasNext();) {
				dp = it.next();
				System.out.println("Endpoint Profile : id=" + dp.getId() + ", name=" +  dp.getName() + ", fqname " + dp.getFqname());
			}
		}
		helper.disconnect();
	}
}