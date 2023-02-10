package com.cisco.pxgrid.samples.ise;

import com.cisco.pxgrid.GridConnection;
import com.cisco.pxgrid.model.core.SubnetContentFilter;
import com.cisco.pxgrid.model.net.Session;

/**
 * Demonstrates how to use an xGrid client to subscribe to and download all active sessions from
 * ISE automatically upon Grid Connection (automation is sustainable upon a ReconnectionManager reconnect).
 * Uses a Session Cache to keep track of active sessions.
 */
public class SessionSubscribeDownload {
	public static void main(String [] args) throws Exception {
		SampleHelper helper = new SampleHelper();
		GridConnection grid = helper.connectWithReconnectionManager();
		
		SubnetContentFilter filter = helper.promptIpFilters("Filters (ex. '1.0.0.0/255.0.0.0,1234::/16,...' or <enter> for no filter): ");

		SessionCache cache = new SessionCache(grid, filter);
		cache.init();
		
		while (true) {		
			String ip = helper.prompt("IP address (or <enter> to disconnect): ");
			if (ip == null) break;
			try {
				Session session = cache.getSession(ip);
				if(session == null) {
					System.out.println("Session not found.");
				}
				else {
					SampleHelper.print(session);
					System.out.println(""); 
				}
			}
			catch (SessionCacheException e) {
				System.out.println("Cache not initialized yet.");
			}
		}
		helper.disconnect();
	}
}
