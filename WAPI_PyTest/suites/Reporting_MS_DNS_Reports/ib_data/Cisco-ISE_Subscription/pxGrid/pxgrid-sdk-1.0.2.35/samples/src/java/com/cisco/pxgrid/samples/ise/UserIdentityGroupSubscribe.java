package com.cisco.pxgrid.samples.ise;

import java.util.List;

import com.cisco.pxgrid.GridConnection;
import com.cisco.pxgrid.model.identity.IdentityGroupNotification;
import com.cisco.pxgrid.model.net.Group;
import com.cisco.pxgrid.model.net.User;
import com.cisco.pxgrid.stub.identity.IdentityGroupNotificationCallback;
import com.cisco.pxgrid.stub.identity.SessionDirectoryFactory;

/**
 * Demonstrates how to use an xGrid client to subscribe to identity group notifications.
 */	
public class UserIdentityGroupSubscribe {
	public static void main(String[] args) throws Exception {
		SampleHelper helper = new SampleHelper();
		GridConnection grid = helper.connectWithReconnectionManager();

		SessionDirectoryFactory.registerNotification(grid, new SampleNotificationHandler());

		helper.prompt("Press <enter> to disconnect...");
		helper.disconnect();
	}
	
	private static class SampleNotificationHandler implements IdentityGroupNotificationCallback {
		@Override
		public void handle(IdentityGroupNotification notf) {
			List<User> users = notf.getUsers();
			if (users != null) {
				for (User user : users) {
					System.out.println("user=" + user.getName());
					for (Group group : user.getGroupList().getObjects()) {
						System.out.println("group=" + group.getName());
					}
				}
			}
		}
		
	}

}

