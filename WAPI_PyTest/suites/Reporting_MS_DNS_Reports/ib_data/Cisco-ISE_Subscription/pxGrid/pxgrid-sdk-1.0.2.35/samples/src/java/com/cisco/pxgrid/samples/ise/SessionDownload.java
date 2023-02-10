package com.cisco.pxgrid.samples.ise;

import java.util.Calendar;

import com.cisco.pxgrid.GridConnection;
import com.cisco.pxgrid.model.core.SubnetContentFilter;
import com.cisco.pxgrid.model.net.Session;
import com.cisco.pxgrid.stub.identity.SessionDirectoryFactory;
import com.cisco.pxgrid.stub.identity.SessionDirectoryQuery;
import com.cisco.pxgrid.stub.identity.SessionIterator;

/**
 * Demonstrates how to use download all active sessions from ISE
 */
public class SessionDownload {
	public static void main(String [] args) throws Exception {
		SampleHelper helper = new SampleHelper();
		GridConnection grid = helper.connectWithReconnectionManager();

		SubnetContentFilter filters = helper.promptIpFilters("Filters (ex. '1.0.0.0/255.0.0.0,1234::/16...' or <enter> for no filter): ");
		Calendar start = helper.promptDate("Start time (ex. '2015-01-31 13:00:00' or <enter> for no start time): ");
		Calendar end = helper.promptDate("End time (ex. '2015-01-31 13:00:00' or <enter> for no end time): ");

		SessionDirectoryQuery sd = SessionDirectoryFactory.createSessionDirectoryQuery(grid);
		SessionIterator iterator = sd.getSessionsByTime(start, end, filters);
		iterator.open();

		int count = 0;
		Session s;
		while ((s = iterator.next()) != null) {
			SampleHelper.print(s);
			count++;
		}
		iterator.close();

		System.out.println("Session count=" + count);
		helper.disconnect();
	}
}
