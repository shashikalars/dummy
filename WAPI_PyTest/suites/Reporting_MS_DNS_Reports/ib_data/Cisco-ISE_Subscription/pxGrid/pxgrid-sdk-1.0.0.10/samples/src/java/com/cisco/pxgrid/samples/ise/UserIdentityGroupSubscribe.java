package com.cisco.pxgrid.samples.ise;

import java.util.List;

import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.ParseException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.cisco.pxgrid.GridConnection;
import com.cisco.pxgrid.ReconnectionManager;
import com.cisco.pxgrid.TLSConfiguration;
import com.cisco.pxgrid.model.identity.IdentityGroupNotification;
import com.cisco.pxgrid.model.net.Group;
import com.cisco.pxgrid.model.net.User;
import com.cisco.pxgrid.stub.identity.IdentityGroupNotificationCallback;
import com.cisco.pxgrid.stub.identity.SessionDirectoryFactory;

/**
 * Demonstrates how to use an xGrid client to subscribe to identity group notifications.
 * 
 * @author jangwin
 *
 */	

public class UserIdentityGroupSubscribe {
	protected static final Logger log = LoggerFactory.getLogger(UserIdentityGroupSubscribe.class);

	public static void main(String[] args)
		throws Exception
	{
		// collect command line parameters using helper class. custom implementations
		// will likely gather this information from a source other than command line.

		SampleProperties props = SampleProperties.load();
		SampleParameters params = new SampleParameters(props);
		params.appendCommonOptions();
		params.appendFilterOption();


		CommandLine line = null;
		try {
			line = params.process(args);
		} catch (IllegalArgumentException e) {
			params.printHelp("session_subscribe");
			System.exit(1);
		} catch (ParseException e) {
			params.printHelp("session_subscribe");
			System.exit(1);
		}

		String[] hostnames = params.retrieveHostnames(line);
		String username = params.retrieveUsername(line);
		String keystoreFilename = params.retrieveKeystoreFilename(line);
		String keystorePassword = params.retrieveKeystorePassword(line);
		String truststoreFilename = params.retrieveTruststoreFilename(line);
		String truststorePassword = params.retrieveTruststorePassword(line);

		System.out.println("------- properties -------");
		System.out.println("version=" + props.getVersion());
		System.out.println("hostnames=" + SampleUtilities.hostnamesToString(hostnames));
		System.out.println("username=" + username);
		System.out.println("keystoreFilename=" + keystoreFilename);
		System.out.println("keystorePassword=" + keystorePassword);
		System.out.println("truststoreFilename=" + truststoreFilename);
		System.out.println("truststorePassword=" + truststorePassword);
		System.out.println("--------------------------");


		// check keystore

		if (!SampleUtilities.isValid(keystoreFilename, keystorePassword)) {
			System.err.println("unable to read keystore. please check the keystore filename and keystore password.");
			System.exit(1);
		}


		// check truststore

		if (!SampleUtilities.isValid(truststoreFilename, truststorePassword)) {
			System.err.println("unable to read truststore. please check the truststore filename and truststore password.");
			System.exit(1);
		}


		// set configuration

		TLSConfiguration config = new TLSConfiguration();
		config.setHosts(hostnames);
		config.setUserName(username);
		config.setGroup(com.cisco.pxgrid.model.ise.Group.SESSION.value());
		config.setKeystorePath(keystoreFilename);
		config.setKeystorePassphrase(keystorePassword);
		config.setTruststorePath(truststoreFilename);
		config.setTruststorePassphrase(truststorePassword);


		// initialize xgrid connection

		GridConnection con = new GridConnection(config);
		con.addListener(new SampleConnectionListener());


		// use reconnection manager to ensure connection gets re-established
		// if dropped. this technique is recommended.

		ReconnectionManager recon = new ReconnectionManager(con);
		recon.setRetryMillisecond(2000);
		recon.start();

		//Register a callback for IdentityGroupNotification
		SessionDirectoryFactory.registerNotification(con, new SampleNotificationHandler());

		// receive notifications until user presses <enter>
		System.out.println("press <enter> to disconnect...");
		System.in.read();


		// disconnect from xGrid. with reconnection manager enabled we only need to call stop.

		recon.stop();
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

