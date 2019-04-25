// Based on: // Based on: https://dike.informatik.uni-wuerzburg.de/summary/projects!unify!apprtc-test.git

package de.lsinfo3.webrtctest;

import org.junit.After;
import org.junit.Test;
import org.openqa.selenium.WebDriver;

import java.net.UnknownHostException;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;

public class AppRTCTest {

    // Video File used for Fake Webcam Input
    private String fakeFile = "/home/christian/Projekt/apprtc-media//Johnny_1280x720_60.y4m"; //TODO Change me for deployment
    // Target Directory to save Statistics etc.
    private String targetDirRoot = "/home/christian/Projekt/apprtc-logs/"; //TODO Change me for deployment
    
    AppRTCUtils util = new AppRTCUtils(fakeFile, targetDirRoot);

    @Test
    public void testJoinAppRTC() throws UnknownHostException {
        String targetDir = util.buildAndMakeTargetDirs();
        
        WebDriver client = util.getChromeDriver(targetDir, true);

        //String room = AppRTC.URL_APPRTC + String.valueOf(new Random().nextInt()).substring(0, 3);
        String room = String.valueOf(new Random().nextInt()).substring(0, 3);
        util.joinSessionAppRTC(client, room);

        util.pause(5);

        util.takeScreenshot(client, targetDir + "/screenieA.png");

        util.openChromeRTCInternals(client);

        util.pause(10);
        util.createChromeRTCDump(client);

        client.close();
        client.quit();
    }
    
    @Test
    public void testJoinJitsi() throws UnknownHostException {
        String targetDir = util.buildAndMakeTargetDirs();
        
        WebDriver clientA = util.getChromeDriver(targetDir, true);

        //String room = String.valueOf(Math.abs(new Random().nextInt())).substring(0, 3);
        String room = "123";
        util.joinSessionJitsi(clientA, room);

        util.pause(5);

        util.takeScreenshot(clientA, targetDir + "screenieA.png");

        util.openChromeRTCInternals(clientA);

        util.pause(10);
        util.createChromeRTCDump(clientA);

        clientA.close();
        clientA.quit();
    }


    @After
    public void tearDown() throws Exception {
    	util.cleanupBrowsers();
    }
}
