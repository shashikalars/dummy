package com.cisco.pxgrid.samples.ise;

import com.cisco.pxgrid.GridConnection.Listener;

/**
 * A simple example showing how to use a connection listener to programmatically
 * react to certain pxGgrid connection events. This class simply prints out
 * messages and exits upon important change events including onDisconnect, onDeleted,
 * and onDisabled.
 * 
 * @author jangwin
 *
 */

public class SampleConnectionListener
	implements Listener
{
	private boolean connected;

	@Override
	public void beforeConnect() {
		System.out.println("connecting...");
	}

	@Override
	public void onConnected() {
		System.out.println("connected.");
		this.connected = true;
	}

	@Override
	public void onDisconnected() {
		if (this.connected) {
			System.out.println("connection closed");
			this.connected = false;
		}
	}

	@Override
	public void onDeleted() {
		System.out.println("account deleted");
	}

	@Override
	public void onDisabled() {
		System.out.println("account disabled");
	}

	@Override
	public void onEnabled() {
		System.out.println("account enabled");
	}

	@Override
	public void onAuthorizationChanged() {
		System.out.println("authorization changed");
	}
}
