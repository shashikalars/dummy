package com.cisco.pxgrid.samples.ise;

import java.lang.Exception;
import com.cisco.pxgrid.model.net.Session;

/**
 * Exception that gets thrown if a Session Cache is queried but has not
 * been initialized yet
 * 
 * @author johamart
 *
 */

public class SessionCacheException extends Exception{
	private Session session;
	
	public SessionCacheException(Session session) {
		super();
		this.session = session;
	}
	
	public Session getSession() {
		return session;
	}
	
}