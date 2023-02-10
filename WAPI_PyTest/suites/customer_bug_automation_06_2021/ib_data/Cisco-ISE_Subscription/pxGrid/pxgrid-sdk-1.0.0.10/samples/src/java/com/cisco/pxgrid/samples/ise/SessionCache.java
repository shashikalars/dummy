package com.cisco.pxgrid.samples.ise;

import java.util.Calendar;
import java.util.Date;
import java.util.Collections;
import java.util.Map;
import java.util.HashMap;
import java.io.IOException;
import java.lang.InterruptedException;

import com.cisco.pxgrid.GCLException;

import java.security.GeneralSecurityException;

import com.cisco.pxgrid.GridConnection;
import com.cisco.pxgrid.model.net.Session;
import com.cisco.pxgrid.stub.identity.SessionDirectoryNotification;
import com.cisco.pxgrid.stub.identity.SessionDirectoryFactory;
import com.cisco.pxgrid.stub.identity.SessionDirectoryQuery;
import com.cisco.pxgrid.stub.identity.SessionIterator;
import com.cisco.pxgrid.model.core.SubnetContentFilter;


/**
 * A cache of active sessions.
 * 
 * @author johamart
 *
 */

public class SessionCache implements SessionDirectoryNotification, GridConnection.Listener {
	private GridConnection con;
	private volatile Map<String, Session> sessions;
	private SubnetContentFilter filter;
	private SessionDirectoryQuery sd;
	private SessionIterator iterator;
	private boolean connected;
	
	public SessionCache(GridConnection con, SubnetContentFilter filter) {
		this.con = con;	
		this.filter = filter;
	}
	
	/**
	 * Initializes the listeners for the cache
	 * @throws GCLException
	 */
	public void init() throws GCLException {
		// Initializes the grid connection listener 
		con.addListener(this);
		//Initializes the session notification listener 
		if (filter != null) {
			SessionDirectoryFactory.registerNotification(con, this, filter);
		} else {
			SessionDirectoryFactory.registerNotification(con, this);
		}
	}
	
	/**
	 * Returns session associated with given IP address
	 * @param ip an IP Address String 
	 * @return returns the Session associated with the IP address, null if doesn't exist
	 * @throws SessionCacheException thrown if cache not yet initialized 
	 */
	public synchronized Session getSession (String ip) throws SessionCacheException {
		if(sessions == null) {
			throw new SessionCacheException(null);
		}
		else {
			return sessions.get(ip);
		}
	}
		
	/**
	 * Callback for a Session notification; session added to cache
	 * @param session the new session notification
	 */
	@Override
	public synchronized void onChange(Session session) {
		// Add session to cache
		String ip = session.getInterface().getIpIntfIDs().get(0).getIpAddress();
		sessions.put(ip, session);
		System.out.println("Session notification added to cache:"); 
		SampleUtilities.print(session);
		System.out.println("");
		System.out.print(">> "); 

	}
	
	/**
	 * Callback for before grid connection
	 */
	@Override
	public synchronized void beforeConnect() {
		// Ignore	
	}
	
	/**
	 * Callback for on grid connection
	 * Cache is initialized, and tries a bulk download
	 * If an exception is thrown while trying to download,
	 * method waits and tries again 
	 */
	@Override
	public synchronized void onConnected() {		
		this.connected = true;
		System.out.println("Connected.");
		sessions = Collections.synchronizedMap(new HashMap<String, Session>());
		System.out.println("New cache initialized.");
		// Try to connect to MnT node
		while(true) {
			try {
				sessionDownload();
				break;
			}
			catch(Exception e) {
				System.out.println("Unable to download sessions, waiting to try again...");
				try {
					Thread.sleep(20000);
				}
				catch(InterruptedException e1) {
				}
			}
			
		}
	}
	
	/**
	 * Callback for grid disconnect
	 * Cache is cleared because data is now stale
	 */
	@Override
	public synchronized void onDisconnected() {
		if (this.connected) {
			System.out.println("Disconnected. Cache cleared.");
			sessions = null;
			this.connected = false;
		}
	}
	
	/**
	 * Callback for account related delete
	 */
	@Override
	public synchronized void onDeleted() {
		// Ignore	
	}
	
	/**
	 * Callback for account related disable
	 */
	@Override
	public synchronized void onDisabled() {
		// Ignore	
	}
	
	/**
	 * Callback for account related enable
	 */
	@Override
	public synchronized void onEnabled() {
		// Ignore
	}
	
	/**
	 * Callback for account related authorization change
	 */
	@Override
	public synchronized void onAuthorizationChanged() {
		// Ignore	
	}
	
	/**
	 * Downloads list of active sessions, adding them to session cache
	 * @throws GCLException
	 * @throws IOException
	 * @throws GeneralSecurityException
	 */
	private void sessionDownload() throws GCLException, IOException, GeneralSecurityException {
		// Construct a date range of requested sessions
		Calendar begin = Calendar.getInstance();
		begin.set(Calendar.YEAR, begin.get(Calendar.YEAR) - 1);
		Calendar end = Calendar.getInstance();
		sd = SessionDirectoryFactory.createSessionDirectoryQuery(con);
		iterator = sd.getSessionsByTime(begin, end, filter);
		iterator.open();
		Date startedAt = new Date();
		System.out.println("starting at " + startedAt.toString() + "...");

		int count = 0;
		Session s = iterator.next();
		while (s != null) {
			String ip = s.getInterface().getIpIntfIDs().get(0).getIpAddress();
			sessions.put(ip, s);
			System.out.println("Session notification added to cache:"); 
			// When testing performance, comment out the following line. otherwise
			// Excessive console IO will adversely affect results
			SampleUtilities.print(s);
			s = iterator.next();
			System.out.println("");
			count++;
			// Prints count number for every 1000 sessions
			if (count % 1000 == 0) {
				System.out.println("count: " + count);
			}
		}

		Date endedAt = new Date();
		System.out.println("... ending at: " + endedAt.toString());

		System.out.println("\n---------------------------------------------------");
		System.out.println("downloaded " + count + " sessions in " + (endedAt.getTime() - startedAt.getTime()) + " milliseconds");
		System.out.println("---------------------------------------------------\n");

		iterator.close();
		System.out.print(">> ");
		
	}
	
	
}