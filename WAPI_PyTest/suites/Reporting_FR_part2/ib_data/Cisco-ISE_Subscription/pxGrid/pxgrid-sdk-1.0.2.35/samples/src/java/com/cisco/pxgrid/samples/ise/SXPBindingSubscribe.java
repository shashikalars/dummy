package com.cisco.pxgrid.samples.ise;

import com.cisco.pxgrid.GridConnection;
import com.cisco.pxgrid.client.identity.sxp.SXPBindingNotificationHandler;
import com.cisco.pxgrid.client.identity.sxp.SXPBindingNotificationManager;
import com.cisco.pxgrid.model.identity.SXPBinding;

public class SXPBindingSubscribe {
	public static void main(String[] args) throws Exception {
		SampleHelper helper = new SampleHelper();
		GridConnection grid = helper.connectWithReconnectionManager();

		SXPBindingNotificationManager manager = new SXPBindingNotificationManager(grid, new SampleNotificationHandler());

		helper.prompt("press <enter> to disconnect...");
		helper.disconnect();
	}

	public static class SampleNotificationHandler
		implements SXPBindingNotificationHandler {

		@Override
		public void add(SXPBinding binding) {
			System.out.print("Binding added: "); 
			SampleHelper.print(binding);
		}

		@Override
		public void delete(SXPBinding binding) {
			System.out.print("Binding deleted: "); 
			SampleHelper.print(binding);
		}
	}
}
