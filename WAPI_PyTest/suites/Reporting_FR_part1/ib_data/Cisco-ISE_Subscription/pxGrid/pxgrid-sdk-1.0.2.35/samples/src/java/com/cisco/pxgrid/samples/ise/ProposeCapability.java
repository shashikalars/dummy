package com.cisco.pxgrid.samples.ise;

import java.util.LinkedList;
import java.util.List;

import com.cisco.pxgrid.GridConnection;
import com.cisco.pxgrid.internal.NotificationCallback;
import com.cisco.pxgrid.model.core.BaseMsg;
import com.cisco.pxgrid.model.core.Capability;
import com.cisco.pxgrid.model.core.CapabilityChangeType;
import com.cisco.pxgrid.model.core.RegisteredCapabilityUpdateNotification;
import com.cisco.pxgrid.stub.core.CoreClientStub;
import com.cisco.pxgrid.stub.core.CoreQuery;

/**
 * Demonstrates how to use a pxGrid client to propose a new capability
 * to pxGrid administrator.
 */
public class ProposeCapability {
	public static void main(String[] args) throws Exception {
		SampleHelper helper = new SampleHelper();
		GridConnection con = helper.connectWithReconnectionManager();

        con.registerTopicChangeCallback(new SampleNotificationCallback());

		CoreClientStub coreClient = new CoreClientStub();
		CoreQuery query = coreClient.createCoreQuery(con);

		String isNew = helper.prompt("New capability? (y/n): " );
		String name = helper.prompt("Enter capability name: ");
		String version = helper.prompt("Enter capability version: ");
		String desc = helper.prompt("Enter capability description: ");		
		String platform = helper.prompt("Enter vendor platform: ");


		List<String> queries = new LinkedList<String>();
		while (true) {
			String queryStr = helper.prompt("Enter query name (<enter> to continue): ");
			if (queryStr == null) break;
			queries.add(queryStr);
		}

		List<String> actions = new LinkedList<String>();
		while (true) {
			String actionStr = helper.prompt("Enter action name (<enter> to continue): ");
			if (actionStr == null) break;
			actions.add(actionStr);
		}

		if ("y".equals(isNew)) {
	        System.out.println("Proposing new capability...");
	        query.proposeCapability(name, version, queries, actions, desc, platform);
		} else {
	        System.out.println("Updating capability...");
		    query.updateCapability(name, version, queries, actions, desc, platform);
		}

        // receive notifications until user presses <enter>
		helper.prompt("Press <enter> to disconnect...");
		helper.disconnect();
	}

    private static void handleCapabilityUpdate(CapabilityChangeType change, Capability cap) {
        System.out.println("change=" + change + "; capability=" + cap.getName() + ", version=" + cap.getVersion());
    }

    public static class SampleNotificationCallback implements NotificationCallback
    {
        @Override
        public void handle(BaseMsg message) {
            RegisteredCapabilityUpdateNotification notif = (RegisteredCapabilityUpdateNotification) message;
            for (Capability cap : notif.getCapabilities()) {
                handleCapabilityUpdate(notif.getChange(), cap);
           }
        }
    }

}
