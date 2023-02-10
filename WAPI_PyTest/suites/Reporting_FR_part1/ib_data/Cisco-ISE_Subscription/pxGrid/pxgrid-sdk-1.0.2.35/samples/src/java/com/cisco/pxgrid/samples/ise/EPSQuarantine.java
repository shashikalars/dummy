package com.cisco.pxgrid.samples.ise;

import com.cisco.pxgrid.GridConnection;
import com.cisco.pxgrid.stub.eps.EPSClientStub;
import com.cisco.pxgrid.stub.eps.EPSQuery;

/**
 * Demonstrates how to use a pxGrid client to invoke an Endpoint Protection
 * Service (EPS) quarantine by IP address in ISE.
 */
public class EPSQuarantine {
	public static void main(String[] args) throws Exception	{
		SampleHelper helper = new SampleHelper();
		GridConnection grid = helper.connectWithReconnectionManager();

		EPSClientStub stub = new EPSClientStub();
		EPSQuery query = stub.createEPSQuery(grid);

		while (true) {
			String ip = helper.prompt("IP address (or <enter> to disconnect): ");
			if (ip == null) break;
			query.quarantineByIP(ip);
		}
		helper.disconnect();
	}
}
