package com.cisco.pxgrid.samples.ise;

import com.cisco.pxgrid.GridConnection;
import com.cisco.pxgrid.model.ise.metadata.EndpointProfile;
import com.cisco.pxgrid.model.ise.metadata.EndpointProfileChangedNotification;
import com.cisco.pxgrid.stub.isemetadata.EndpointProfileClientStub;
import com.cisco.pxgrid.stub.isemetadata.EndpointProfileNotification;

public class EndpointProfileMetaDataSubscribe {
	public static void main(String[] args) throws Exception {
		SampleHelper helper = new SampleHelper();
		GridConnection grid = helper.connectWithReconnectionManager();


		EndpointProfileClientStub stub = new EndpointProfileClientStub(grid);
		stub.registerNotification(new SampleNotificationCallback());
		
		helper.prompt("Press <enter> to disconnect...");
		helper.disconnect();
	}

	
	public static class SampleNotificationCallback implements EndpointProfileNotification
	{
		@Override
		public void handle(EndpointProfileChangedNotification notif) {
			EndpointProfile dp = notif.getEndpointProfile();
			System.out.println("EndpointProfileChangedNotification (changetype=" + notif.getChangeType() + ") Device profile : id="
					+ dp.getId() + ", name=" +
					dp.getName() + ", fqname=" + dp.getFqname());
					
		}
	}
}