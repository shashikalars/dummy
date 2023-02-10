/*******************************************************************************
 * Copyright (c) 2015 Cisco Systems, Inc.
 * All rights reserved.
 *******************************************************************************/

package com.cisco.pxgrid.samples.ise;

import java.util.Iterator;
import java.util.LinkedHashSet;
import java.util.Set;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;

import com.cisco.pxgrid.CapabilityRef;
import com.cisco.pxgrid.GCLException;
import com.cisco.pxgrid.GridConnection;
import com.cisco.pxgrid.internal.NotificationCallback;
import com.cisco.pxgrid.internal.QueryCallback;
import com.cisco.pxgrid.model.core.BaseError;
import com.cisco.pxgrid.model.core.BaseMsg;
import com.cisco.pxgrid.model.core.GenericMessage;
import com.cisco.pxgrid.model.core.GenericMessageContent;
import com.cisco.pxgrid.model.core.GenericMessageContentType;
import com.cisco.pxgrid.model.core.GenericMessageType;
import com.cisco.pxgrid.util.GenericMessageBuilder;
import com.cisco.pxgrid.util.GenericMessageContentExtractor;

/**
 * @author anto
 *
 */
public class GenericClient {

    private static final String TOPIC_NAME        = "topic-name";
    private static final String CLIENT_MODE       = "client-mode";
    private static final String QUERY_NAME_SET    = "query-name-set";
    private static final String ACTION_NAME_SET   = "action-name-set";
    private static final String PUBLISH_DATA_SET  = "publish-data-set";
    private static final String REQUEST_DATA_SET  = "request-data-set";
    private static final String RESPONSE_DATA_SET = "response-data-set";
    private static final String SLEEP_INTERVAL    = "sleep-interval";
    private static final String ITERATIONS        = "iterations";

    enum ClientMode {
        PUBLISHER("publisher", "_Publish"), SUBSCRIBER("subscriber", "_Subscribe"), ACTION("action", "_Action");

        private String value;
        private String groupSuffix;

        ClientMode(String value, String groupSuffix) {
            this.value = value;
            this.groupSuffix = groupSuffix;
        }

        String groupName(String topicName) {
            return topicName + groupSuffix;
        }

        static ClientMode fromValue(String value) {
            ClientMode mode = null;

            for (ClientMode m : ClientMode.values()) {
                if (m.value.equalsIgnoreCase(value)) {
                    mode = m;
                    break;
                }
            }

            return mode;
        }
    }

    private String          topicName;
    private ClientMode      clientMode;
    private int             sleepInterval;
    private int             iterations;
    private Set<String>     queryNameSet    = new LinkedHashSet<String>();
    private Set<String>     actionNameSet   = new LinkedHashSet<String>();
    private Set<String>     publishDataSet  = new LinkedHashSet<String>();
    private Set<String>     requestDataSet  = new LinkedHashSet<String>();
    private Set<String>     responseDataSet = new LinkedHashSet<String>();

    private CapabilityRef   capRef;
    private SampleHelper    helper          = null;
    private GridConnection  gridConnection  = null;

    private ExecutorService taskExecutor    = null;

    public GenericClient() {
        super();
    }

    public void init(String[] args) {

        topicName = System.getProperty(TOPIC_NAME);
        if (topicName == null) {
            System.out.println("the " + TOPIC_NAME + " property is not valid - cannot proceed without topic name");
            throw new RuntimeException("property " + TOPIC_NAME + " must be specified");
        }
        capRef = new CapabilityRef(topicName);

        String clientModeStr = System.getProperty(CLIENT_MODE);
        clientMode = ClientMode.fromValue(clientModeStr);
        if (clientMode == null) {
            System.out.println("the " + CLIENT_MODE + " property is not valid - using " + ClientMode.SUBSCRIBER.value);
            clientMode = ClientMode.SUBSCRIBER;
        }

        sleepInterval = Integer.parseInt(System.getProperty(SLEEP_INTERVAL, "500"));
        iterations = Integer.parseInt(System.getProperty(ITERATIONS, "20"));

        String dataText = System.getProperty(QUERY_NAME_SET, "query-001,query-002,query-003");
        for (String d : dataText.split(",")) {
            queryNameSet.add(d);
        }

        dataText = System.getProperty(ACTION_NAME_SET, "act-001,act-002");
        for (String d : dataText.split(",")) {
            actionNameSet.add(d);
        }

        dataText = System.getProperty(PUBLISH_DATA_SET, "pub-data-001,pub-data-002");
        for (String d : dataText.split(",")) {
            publishDataSet.add(d);
        }

        dataText = System.getProperty(REQUEST_DATA_SET, "req-data-001,req-data-002");
        for (String d : dataText.split(",")) {
            requestDataSet.add(d);
        }

        dataText = System.getProperty(RESPONSE_DATA_SET, "resp-data-001,resp-data-002");
        for (String d : dataText.split(",")) {
            responseDataSet.add(d);
        }
        System.out.println("Initialized : " + displayString());
    }

    public String displayString() {
        StringBuilder builder = new StringBuilder();
        builder.append("GenericClient:");
        builder.append("\n\ttopicName=");
        builder.append(topicName);
        builder.append("\n\tclientMode=");
        builder.append(clientMode);
        builder.append("\n\tsleepInterval=");
        builder.append(sleepInterval);
        builder.append("\n\titerations=");
        builder.append(iterations);
        builder.append("\n\tqueryNameSet=");
        builder.append(queryNameSet);
        builder.append("\n\tactionNameSet=");
        builder.append(actionNameSet);
        builder.append("\n\tpublishDataSet=");
        builder.append(publishDataSet);
        builder.append("\n\trequestDataSet=");
        builder.append(requestDataSet);
        builder.append("\n\tresponseDataSet=");
        builder.append(responseDataSet);
        builder.append("\n");
        return builder.toString();
    }

    private static String displayMessage(BaseMsg msg) {
        String messageText = null;

        if (msg instanceof GenericMessage) {
            GenericMessage message = (GenericMessage) msg;

            StringBuilder builder = new StringBuilder("GenericMessage:");
            builder.append("\n  messageType=").append(message.getMessageType());
            builder.append("\n  capabilityName=").append(message.getCapabilityName());
            builder.append("\n  operationName=").append(message.getOperationName());

            builder.append("\n  body:");
            for (GenericMessageContent content : message.getBody()) {
                builder.append("\n    content:");
                builder.append("\n      contentTags=").append(content.getContentTags());
                builder.append("\n      contentType=").append(content.getContentType());
                builder.append("\n      value=");
                GenericMessageContentExtractor extractor = GenericMessageContentExtractor.newExtractor(content);
                switch (content.getContentType()) {
                case PLAIN_TEXT:
                    builder.append(extractor.extractPlainText());
                    break;

                default:
                    builder.append(extractor.extractRaw());
                    break;
                }
            }

            if (message.getError() != null) {
                builder.append("\n  error=").append(message.getError().getDescription());
            }
            messageText = builder.toString();
        } else {
            messageText = String.valueOf(msg);
        }

        return messageText;
    }

    private void runAsPublisher() throws Exception {
        gridConnection.registerRequestHandler(capRef, new MyRequestHandler());
        gridConnection.publishCapability(capRef);
        Future<?> f = taskExecutor.submit(new PublisherTask());
        f.get();
    }

    private void runAsActionClient() throws Exception {
        RequestTask task = new RequestTask("ACTION", actionNameSet, requestDataSet);
        Future<?> f = taskExecutor.submit(task);
        f.get();
    }

    private void runAsSubscriber() throws Exception {
        gridConnection.subscribeCapability(capRef, new MyNotificationHandler());
        RequestTask task = new RequestTask("QUERY", queryNameSet, requestDataSet);
        Future<?> f = taskExecutor.submit(task);
        f.get();
    }

    private void run() throws Exception {
        taskExecutor = Executors.newSingleThreadExecutor();

        System.setProperty(SampleHelper.PROP_GROUP, clientMode.groupName(topicName));
        helper = new SampleHelper();
        gridConnection = helper.connectWithReconnectionManager();

        switch (clientMode) {
        case PUBLISHER:
            runAsPublisher();
            break;

        case SUBSCRIBER:
            runAsSubscriber();
            break;

        case ACTION:
            runAsActionClient();
            break;

        default:
            break;
        }

        // sleep a bit longer to allow a few more messages
        Thread.sleep(sleepInterval * 4);

        // receive notifications until user presses <enter>
        helper.prompt("Press <enter> to disconnect...");
        helper.disconnect();

        taskExecutor.shutdown();
    }

    static class MyNotificationHandler implements NotificationCallback {

        @Override
        public void handle(BaseMsg message) {
            System.out.println("Received notification: " + displayMessage(message));
        }

    }

    class MyRequestHandler implements QueryCallback {
        private Iterator<String> respDataIt;

        MyRequestHandler() {
            respDataIt = responseDataSet.iterator();
        }

        private String getNextResponseData() {
            if (!respDataIt.hasNext()) {
                respDataIt = responseDataSet.iterator();
            }
            return respDataIt.next();
        }

        @Override
        public BaseMsg handle(BaseMsg message) {
            System.out.println("Received request: " + displayMessage(message));
            GenericMessage response = new GenericMessage();
            response.setCapabilityName(topicName);
            response.setMessageType(GenericMessageType.RESPONSE);

            if (message instanceof GenericMessage) {
                GenericMessage request = (GenericMessage) message;
                if (request.getMessageType() != GenericMessageType.REQUEST) {
                    BaseError error = new BaseError();
                    error.setDescription("Unable to handle the request received - GenericMessageType is not REQUEST");
                    response.setError(error);
                } else {

                    StringBuilder scratch = new StringBuilder("RESPONSE[");
                    scratch.append(System.currentTimeMillis()).append("]");
                    scratch.append(getNextResponseData()).append(" - for request[");
                    for (GenericMessageContent reqContent : request.getBody()) {
                        if (reqContent.getContentType() == GenericMessageContentType.PLAIN_TEXT) {
                            scratch.append(new String(reqContent.getValue()));
                        }
                    }
                    scratch.append("]");

                    GenericMessageBuilder responseBuilder = GenericMessageBuilder.responseBuilder(topicName, request.getOperationName());
                    responseBuilder.addPlainTextContent(scratch.toString(), "RESP-TAG-101");
                    response = responseBuilder.build();

                    // GenericMessageContent content = new GenericMessageContent();
                    // content.getContentTags().add("RESP-TAG-101");
                    // content.setContentType(GenericMessageContentType.PLAIN_TEXT);
                    // content.setValue(scratch.toString().getBytes());
                    //
                    // response.setOperationName(request.getOperationName());
                    // response.getBody().add(content);
                }
            } else {
                BaseError error = new BaseError();
                error.setDescription("Unable to handle the request received - not a GenericMessage type");
                response.setError(error);
            }

            System.out.println("Returning response: " + displayMessage(response));
            return response;
        }
    }

    class PublisherTask implements Runnable {
        private Iterator<String> pubDataIt;
        private int              count;

        PublisherTask() {
            pubDataIt = publishDataSet.iterator();
            count = 0;
        }

        private String getNextPubData() {
            if (!pubDataIt.hasNext()) {
                pubDataIt = publishDataSet.iterator();
            }
            return pubDataIt.next();
        }

        private void publishData() throws GCLException {
            StringBuilder scratch = new StringBuilder("NOTIFICATION[");
            scratch.append(System.currentTimeMillis()).append("]");
            scratch.append(getNextPubData());

            GenericMessageBuilder builder = GenericMessageBuilder.notificationBuilder(topicName, "sampleNotification");
            GenericMessage notif = builder.addPlainTextContent(scratch.toString(), "NOTIF-TAG-201").build();

            // GenericMessageContent content = new GenericMessageContent();
            // content.getContentTags().add("NOTIF-TAG-201");
            // content.setContentType(GenericMessageContentType.PLAIN_TEXT);
            // content.setValue(scratch.toString().getBytes());
            //
            // GenericMessage notif = new GenericMessage();
            // notif.setCapabilityName(topicName);
            // notif.setMessageType(GenericMessageType.NOTIFICATION);
            // notif.getBody().add(content);

            if (gridConnection != null) {
                System.out.println("Publishing notification: " + displayMessage(notif));
                gridConnection.notify(capRef, notif);
            }
        }

        @Override
        public void run() {
            try {
                while (count < iterations) {
                    count++;
                    publishData();
                    Thread.sleep(sleepInterval);
                }
            } catch (Exception e) {
                System.err.println("Error while publishing : " + e);
            }
        }

    }

    class RequestTask implements Runnable {
        private Set<String>      nameSet;
        private Set<String>      dataSet;
        private Iterator<String> nameIt;
        private Iterator<String> dataIt;
        private int              count;
        private String           tag;

        RequestTask(String tag, Set<String> nameSet, Set<String> dataSet) {
            this.tag = tag;
            this.nameSet = nameSet;
            this.dataSet = dataSet;
            nameIt = nameSet.iterator();
            dataIt = dataSet.iterator();
            count = 0;
        }

        private String getNextName() {
            if (!nameIt.hasNext()) {
                nameIt = nameSet.iterator();
            }
            return nameIt.next();
        }

        private String getNextData() {
            if (!dataIt.hasNext()) {
                dataIt = dataSet.iterator();
            }
            return dataIt.next();
        }

        private void sendRequest() throws GCLException {
            StringBuilder scratch = new StringBuilder(tag).append("[");
            scratch.append(System.currentTimeMillis()).append("]");
            scratch.append(getNextData());
            
            GenericMessageBuilder builder = GenericMessageBuilder.requestBuilder(topicName, getNextName());
            GenericMessage request = builder.addPlainTextContent(scratch.toString(), tag + "-TAG-301").build();

            // GenericMessageContent content = new GenericMessageContent();
            // content.getContentTags().add(tag + "-TAG-301");
            // content.setContentType(GenericMessageContentType.PLAIN_TEXT);
            // content.setValue(scratch.toString().getBytes());
            //
            // GenericMessage request = new GenericMessage();
            // request.setCapabilityName(topicName);
            // request.setMessageType(GenericMessageType.REQUEST);
            // request.setOperationName(getNextName());
            // request.getBody().add(content);

            if (gridConnection != null) {
                System.out.println("Sending request: " + displayMessage(request));
                BaseMsg resp = gridConnection.query(capRef, request);
                System.out.println("Received response: " + displayMessage(resp));
            }
        }

        @Override
        public void run() {
            try {
                while (count < iterations) {
                    count++;
                    try {
                    	sendRequest();
                    } catch (Exception e) {
                        System.err.println("Error while sending request : " + e);
                    }
                    Thread.sleep(sleepInterval);
                }
            } catch (Exception e) {
                System.err.println("Thread got interrupted : " + e);
            }
        }

    }

    /**
     * @param args
     */
    public static void main(String[] args) {
        GenericClient client = new GenericClient();
        client.init(args);
        try {
            client.run();
        } catch (Exception e) {
            System.err.println("Error while running client : " + e);
        }
    }

}
