package com.cisco.pxgrid.samples.ise;

import java.util.Scanner;

import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.ParseException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.cisco.pxgrid.GridConnection;
import com.cisco.pxgrid.ReconnectionManager;
import com.cisco.pxgrid.TLSConfiguration;
import com.cisco.pxgrid.samples.ise.SessionCache;
import com.cisco.pxgrid.model.core.SubnetContentFilter;
import com.cisco.pxgrid.model.ise.Group;
import com.cisco.pxgrid.model.net.Session;

/**
 * Demonstrates how to use an xGrid client to subscribe to and download all active sessions from
 * ISE automatically upon Grid Connection (automation is sustainable upon a ReconnectionManager reconnect).
 * Uses a Session Cache to keep track of active sessions.
 * 
 * @author johamart
 *
 */

public class SessionSubscribeDownload {
	protected static final Logger log = LoggerFactory.getLogger(SessionSubscribeDownload.class);

	public static void main(String [] args)
		throws Exception
	{
		// Collect command line parameters using helper class. custom implementations
		// Will likely gather this information from a source other than command line.

		SampleProperties props = SampleProperties.load();
		SampleParameters params = new SampleParameters(props);
		params.appendCommonOptions();
		params.appendFilterOption();

		CommandLine line = null;
		try {
			line = params.process(args);
		} catch (IllegalArgumentException e) {
			params.printHelp("session_download");
			System.exit(1);
		} catch (ParseException e) {
			params.printHelp("session_download");
			System.exit(1);
		}


		String[] hostnames = params.retrieveHostnames(line);
		String username = params.retrieveUsername(line);
		String keystoreFilename = params.retrieveKeystoreFilename(line);
		String keystorePassword = params.retrieveKeystorePassword(line);
		String truststoreFilename = params.retrieveTruststoreFilename(line);
		String truststorePassword = params.retrieveTruststorePassword(line);
		SubnetContentFilter filter = params.retrieveFilter(line);
		String filterStr = params.retrieveFilterStr(line);

		System.out.println("------- properties -------");
		System.out.println("version=" + props.getVersion());
		System.out.println("hostnames=" + SampleUtilities.hostnamesToString(hostnames));
		System.out.println("username=" + username);
		System.out.println("keystoreFilename=" + keystoreFilename);
		System.out.println("keystorePassword=" + keystorePassword);
		System.out.println("truststoreFilename=" + truststoreFilename);
		System.out.println("truststorePassword=" + truststorePassword);
		System.out.println("filter=" + filterStr);
		System.out.println("--------------------------");


		// Check keystore

		if (!SampleUtilities.isValid(keystoreFilename, keystorePassword)) {
			System.err.println("unable to read keystore. please check the keystore filename and keystore password.");
			System.exit(1);
		}


		// Check truststore

		if (!SampleUtilities.isValid(truststoreFilename, truststorePassword)) {
			System.err.println("unable to read truststore. please check the truststore filename and truststore password.");
			System.exit(1);
		}


		// Assemble configuration

		TLSConfiguration config = new TLSConfiguration();
		config.setHosts(hostnames);
		config.setUserName(username);
		config.setGroup(Group.SESSION.value());
		config.setKeystorePath(keystoreFilename);
		config.setKeystorePassphrase(keystorePassword);
		config.setTruststorePath(truststoreFilename);
		config.setTruststorePassphrase(truststorePassword);


		// Initialize xgrid connection

		GridConnection con = new GridConnection(config);

		// Use reconnection manager to ensure connection gets re-established
		// if dropped. This technique is recommended.
		ReconnectionManager recon = new ReconnectionManager(con);
		recon.setRetryMillisecond(2000);
		
		// Initialize the SessionCache
		SessionCache cache = new SessionCache(con, filter);
		cache.init();
		
		// Start reconnection manager
		recon.start();
		while (!con.isConnected()) {
			Thread.sleep(100);
		}	
		// Query sessions based on user input (ip address)
		Scanner scanner = new Scanner(System.in);
		System.out.println("ip address (or <enter> to disconnect): ");
		while (true) {		
			System.out.print(">> ");
			String ip = scanner.nextLine();

			if (ip == null || "".equals(ip)) {
				break;
			}
			try {
				Session session = cache.getSession(ip);
				if(session == null) {
					System.out.println("Session not found.");
				}
				else {
					SampleUtilities.print(session);
					System.out.println(""); 
				}
			}
			catch(SessionCacheException e) {
				System.out.println("Cache not initialized yet.");
			}
		}
		scanner.close();
		// Disconnect from xGrid. With reconnection manager enabled we only need to call stop.
		recon.stop();

		
	}
}