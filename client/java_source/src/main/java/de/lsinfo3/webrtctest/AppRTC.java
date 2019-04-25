// Based on: https://dike.informatik.uni-wuerzburg.de/summary/projects!unify!apprtc-test.git

package de.lsinfo3.webrtctest;


import java.net.Inet4Address;
import java.net.UnknownHostException;
import java.util.Random;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
//import org.apache.commons.cli.*;


public class AppRTC {
	
	public AppRTC() {
		
	}

    public static final String LOC_MSG_RDY = "lsinfo3";

    //public static final By teee = By.

    public static final By LOC_BTN_JOIN = By.id("confirm-join-button");
    public static final By LOC_BTN_CREATE_DUMP = By.tagName("summary");
    public static final By LOC_BTN_DL_PEERCON = By.tagName("button");

    public static final String URL_APPRTC = "https://appr.tc/r/webrtcproject";
    public static final String URL_JITSI = "https://meet.jit.si/lsinfo3";
    
    // Video File used for Fake Webcam Input
	private static String fakeFile = "/home/webrtc/apprtc-media//Johnny_1280x720_60.y4m";
	
    // Target Directory to save statistics etc.
    private static String targetDirRoot = "/home/webrtc/apprtc-logs/";
    
    public static void main(String[] args) throws UnknownHostException {
    	
    	//Options options = new Options();
    	
    	
    	String room;
    	int duration = 120;
    	if (args.length == 2) {
    		System.out.println("Using given room number + modified session duration");
    		room = args[0];
    		duration = Integer.parseInt(args[1]);
    	}
    	else if (args.length == 1) {
    		room = args[0];
    		System.out.println("Using given room number");
    		//System.out.println(AppRTC.URL_APPRTC + room);
    		System.out.println(AppRTC.URL_JITSI + room);
    	} else if (args.length == 0)  {
    		System.out.println("Using randomized room number");
    		room = String.valueOf(Math.abs(new Random().nextInt())).substring(0, 3);
    		//System.out.println(AppRTC.URL_APPRTC + room);
    		System.out.println(AppRTC.URL_JITSI + room);
    	} else {
    		System.out.println("Invalid number of arguments given, please specify exactly one or zero arguments");
    		return;
    	}
    	
    	
    	System.out.println("");
    	System.out.println("Using fakeFile: " + fakeFile);
    	System.out.println("Using targetDirRoot: " + targetDirRoot);
    	System.out.println("");
    	
    	
    	AppRTCUtils util = new AppRTCUtils(fakeFile, targetDirRoot);
    	
    	String targetDir = util.buildAndMakeTargetDirs();
    	WebDriver client = util.getChromeDriver(targetDir, true);
    	
    	//util.joinSessionAppRTC(client, room);
    	util.joinSessionJitsi(client, room);
    	
    	util.pause(20);
        util.takeScreenshot(client, targetDir + "screenieA.png");
        util.openChromeRTCInternals(client);
        util.pause(duration);
        util.createChromeRTCDump(client);
        util.pause(5);
        client.close();
        client.quit();
        
        System.out.println("Done!");
    }
}
