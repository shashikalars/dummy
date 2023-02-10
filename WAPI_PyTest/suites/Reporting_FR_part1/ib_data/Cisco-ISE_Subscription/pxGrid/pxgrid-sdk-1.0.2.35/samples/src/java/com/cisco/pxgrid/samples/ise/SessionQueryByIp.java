package com.cisco.pxgrid.samples.ise;

import java.net.InetAddress;

import com.cisco.pxgrid.GridConnection;
import com.cisco.pxgrid.model.net.Session;
import com.cisco.pxgrid.stub.identity.SessionDirectoryFactory;
import com.cisco.pxgrid.stub.identity.SessionDirectoryQuery;

/**
 * Demonstrates how to query ISE for an active session by IP address
 */
public class SessionQueryByIp {
	public static void main(String[] args) throws Exception {
		SampleHelper helper = new SampleHelper();
		GridConnection grid = helper.connectWithReconnectionManager();

		SessionDirectoryQuery query = SessionDirectoryFactory
				.createSessionDirectoryQuery(grid);

		while (true) {
			String ip = helper.prompt("IP address (or <enter> to disconnect): ");
			if (ip == null)	break;

			Session session = query.getActiveSessionByIPAddress(InetAddress
					.getByName(ip));
			if (session != null) {
				SampleHelper.print(session);
			} else {
				System.out.println("session not found");
			}
		}
		helper.disconnect();
	}
}
