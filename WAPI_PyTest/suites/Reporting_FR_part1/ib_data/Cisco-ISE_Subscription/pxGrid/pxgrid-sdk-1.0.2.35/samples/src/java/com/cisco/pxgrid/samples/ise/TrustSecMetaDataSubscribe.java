package com.cisco.pxgrid.samples.ise;

import com.cisco.pxgrid.GridConnection;
import com.cisco.pxgrid.model.ise.metadata.SecurityGroup;
import com.cisco.pxgrid.model.ise.metadata.SecurityGroupChangeNotification;
import com.cisco.pxgrid.stub.isemetadata.SecurityGroupNotification;
import com.cisco.pxgrid.stub.isemetadata.TrustSecClientStub;

public class TrustSecMetaDataSubscribe {
	public static void main(String[] args) throws Exception {
		SampleHelper helper = new SampleHelper();
		GridConnection grid = helper.connectWithReconnectionManager();

		TrustSecClientStub stub = new TrustSecClientStub(grid);
		stub.registerNotification(new SampleNotificationCallback());

		helper.prompt("Press <enter> to disconnect...");
		helper.disconnect();
	}

	public static class SampleNotificationCallback implements
			SecurityGroupNotification {
		@Override
		public void handle(SecurityGroupChangeNotification notif) {
			SecurityGroup sg = notif.getSecurityGroup();
			System.out.println("SecurityGroupChangeNotification (changetype="
					+ notif.getChangeType() + ") SecurityGroup : id="
					+ sg.getId() + ", name=" + sg.getName() + ", desc="
					+ sg.getDescription() + ", tag=" + sg.getTag());
		}
	}
}
