package com.cisco.pxgrid.samples.ise;

import com.cisco.pxgrid.GridConnection;
import com.cisco.pxgrid.stub.eps.EPSClientStub;
import com.cisco.pxgrid.stub.eps.EPSQuery;

/**
 * Demonstrates how to use a pxGrid client to invoke an Endpoint Protection
 * Service (EPS) unquarantine by MAC address in ISE.
 */
public class EPSUnquarantine {
	public static void main(String[] args) throws Exception {
		SampleHelper helper = new SampleHelper();
		GridConnection grid = helper.connectWithReconnectionManager();

		EPSClientStub stub = new EPSClientStub();
		EPSQuery query = stub.createEPSQuery(grid);

		while (true) {
			String mac = helper.prompt("MAC address (or <enter> to disconnect): ");
			if (mac == null)	break;
			query.unquarantineByMAC(mac);
		}
		helper.disconnect();
	}
}
