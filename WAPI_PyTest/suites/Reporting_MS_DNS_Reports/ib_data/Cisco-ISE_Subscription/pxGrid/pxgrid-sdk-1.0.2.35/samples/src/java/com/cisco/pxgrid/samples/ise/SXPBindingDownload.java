package com.cisco.pxgrid.samples.ise;

import com.cisco.pxgrid.GridConnection;
import com.cisco.pxgrid.client.identity.sxp.SXPBindingIterator;
import com.cisco.pxgrid.client.identity.sxp.SXPBindingQuery;
import com.cisco.pxgrid.model.identity.SXPBinding;

/**
 * Demonstrates how to use download all active sessions from ISE
 */
public class SXPBindingDownload {
	public static void main(String [] args) throws Exception {
		SampleHelper helper = new SampleHelper();
		GridConnection grid = helper.connectWithReconnectionManager();

		SXPBindingQuery query = new SXPBindingQuery(grid);
		SXPBindingIterator iterator = query.getAllLocalAndLearnedBindings();

		int count = 0;
		SXPBinding s;
		while ((s = iterator.next()) != null) {
			SampleHelper.print(s);
			count++;
		}
		iterator.close();

		System.out.println("Binding count=" + count);
		helper.disconnect();
	}
}
