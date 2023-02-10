/**
 * Copyright (c) 2015 Cisco Systems, Inc.
 * All rights reserved.
 */
package com.cisco.pxgrid.samples.ise;

import com.cisco.pxgrid.GridConnection;
import com.cisco.pxgrid.internal.NotificationCallback;
import com.cisco.pxgrid.model.core.BaseMsg;
import com.cisco.pxgrid.model.core.BaseMsgReference;
import com.cisco.pxgrid.model.core.Capability;
import com.cisco.pxgrid.model.core.CapabilityChangeType;
import com.cisco.pxgrid.model.core.MethodPermissions;
import com.cisco.pxgrid.model.core.RegisteredAndPendingStatus;
import com.cisco.pxgrid.model.core.RegisteredCapabilityUpdateNotification;

/**
 * Sample class to demonstrate subscribing to Core Capability and registering for notifications
 */
public class CoreCapabilitySubscribe {
    public static void main(String[] args) throws Exception {
        SampleHelper helper = new SampleHelper();
        GridConnection grid = helper.connectWithReconnectionManager();
        grid.registerTopicChangeCallback(new SampleNotificationCallback());

        // Query for all registered capabilities.
        for (Capability cap : grid.getRegisteredCapabilitiesList()) {
            printCapabilityAndState("getList", CapabilityChangeType.CREATED, cap);
        }


        // Query a single capability specified by user.
        while (true) {
            final String capNameAndVersion = helper.prompt("Capability name [, version] to query (or <enter> to quit) : ");
            if (capNameAndVersion == null || capNameAndVersion.isEmpty()) {
                break;
            }
            String[] input = capNameAndVersion.split(",");
            final String capName = input[0].trim();
            String capVersion = null;
            if (input.length > 1) {
                capVersion = input[1].trim();
            }

            RegisteredAndPendingStatus status = grid.getCapabilityStatus(capName, capVersion);

            if (status.getTopicStatus() != null) {
                printCapabilityAndState("topicStatus", status.getTopicStatus().getStatus(), status.getTopicStatus().getCapability());
            }
            if (status.getPendingStatus() != null) {
                printCapabilityAndState("pendingStatus", status.getPendingStatus().getStatus(), status.getPendingStatus().getCapability());
            }
        }

        helper.disconnect();
    }

    private static void printCapabilityAndState(final String prefix, CapabilityChangeType status, Capability cap) {
        if (cap != null) {
            StringBuilder out = new StringBuilder();
            out.append(prefix).append(": status=").append(status);
            out.append(" capability=").append(cap.getName());
			out.append(", version=").append(cap.getVersion());
			out.append(cap.getDescription() != null && !cap.getDescription().isEmpty() ? ", description=" + cap.getDescription():"");
			out.append(cap.getVendorPlatform() != null && !cap.getVendorPlatform().isEmpty() ? ", platform=" + cap.getVendorPlatform():"");
			String delimiter = ", operations=";
			for(BaseMsgReference ref:cap.getQueryMethods()){
				out.append(delimiter).append(ref.getMethodName());
				out.append(ref.getMethodPermissions() == MethodPermissions.READ_ONLY ? "(R)" : "(W)" );
				delimiter = ", ";
			}
			System.out.println(out);
        } else {
            System.out.println(prefix + ": status=" + status);
        }
    }

    public static class SampleNotificationCallback implements NotificationCallback {
        @Override
        public void handle(BaseMsg msg) {
            RegisteredCapabilityUpdateNotification notif = (RegisteredCapabilityUpdateNotification) msg;
            for (Capability cap : notif.getCapabilities()) {
                 printCapabilityAndState("notification", notif.getChange(), cap);
            }
        }
    }
}
