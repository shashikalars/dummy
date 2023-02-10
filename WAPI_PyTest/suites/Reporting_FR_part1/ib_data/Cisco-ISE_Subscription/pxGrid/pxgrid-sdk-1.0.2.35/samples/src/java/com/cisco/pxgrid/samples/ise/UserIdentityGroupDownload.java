package com.cisco.pxgrid.samples.ise;

import com.cisco.pxgrid.GridConnection;
import com.cisco.pxgrid.model.net.User;
import com.cisco.pxgrid.stub.identity.IdentityGroupQuery;
import com.cisco.pxgrid.stub.identity.Iterator;
import com.cisco.pxgrid.stub.identity.SessionDirectoryFactory;

/**
 * Demonstrates how to download all identity groups in ISE
 */
public class UserIdentityGroupDownload {
	public static void main(String [] args)	throws Exception {
		SampleHelper helper = new SampleHelper();
		GridConnection grid = helper.connectWithReconnectionManager();

		IdentityGroupQuery sd = SessionDirectoryFactory.createIdentityGroupQuery(grid);
		Iterator<User> iterator = sd.getIdentityGroups();
		iterator.open();

		int count = 0;
		User s;
		while ((s = iterator.next()) != null) {
			System.out.println("user=" + s.getName() + " groups=" + s.getGroupList().getObjects().get(0).getName());
			count++;
		}
		iterator.close();

		System.out.println("User count=" + count);
		helper.disconnect();
	}
}
