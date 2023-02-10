package com.cisco.pxgrid.samples.ise;

import com.cisco.pxgrid.GridConnection;
import com.cisco.pxgrid.model.net.Group;
import com.cisco.pxgrid.model.net.User;
import com.cisco.pxgrid.stub.identity.IdentityGroupQuery;
import com.cisco.pxgrid.stub.identity.SessionDirectoryFactory;

/**
 * Demonstrates how to use an xGrid client to query an identity group.
 */
public class UserIdentityGroupQuery {
	public static void main(String[] args) throws Exception	{
		SampleHelper helper = new SampleHelper();
		GridConnection grid = helper.connectWithReconnectionManager();

		IdentityGroupQuery idGroupQuery = SessionDirectoryFactory.createIdentityGroupQuery(grid);

		while (true) {
			String user = helper.prompt("user name (or <enter> to disconnect): ");
			if (user == null) break;

			User u = idGroupQuery.getIdentityGroupByUser(user);
			if (u != null) {
				for (Group group : u.getGroupList().getObjects()) {
					System.out.println("group=" + group.getName());
				}
			} else {
				System.out.println("no groups associated with this user or no session activity associated with this user");
			}
		}
		helper.disconnect();
	}
}
