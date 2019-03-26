package de.lsinfo3.webrtctest;

import java.io.File;
import java.io.IOException;
import java.net.Inet4Address;
import java.net.InetAddress;
import java.net.UnknownHostException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Set;
import java.util.concurrent.TimeUnit;

import org.apache.commons.io.FileUtils;
import org.openqa.selenium.By;
import org.openqa.selenium.Dimension;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.Keys;
import org.openqa.selenium.OutputType;
import org.openqa.selenium.TakesScreenshot;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;

public class AppRTCUtils {
	
	List<WebDriver> browsers = new ArrayList<WebDriver>();
	
	private String fakeFile;
    private String targetDirRoot;
    
	public AppRTCUtils(String fakeFile, String targetDirRoot) {
		super();
		this.fakeFile = fakeFile;
		this.targetDirRoot = targetDirRoot;
	}
	
	public void createDirs(String targetDir) throws UnknownHostException {
		String IP = Inet4Address.getLocalHost().getHostAddress();
		String targetFile = targetDir + "/" + IP;
		File f = new File(targetFile);
        Path path = Paths.get(targetDir);
        if(!Files.exists(path)) {
            try {
                Files.createDirectories(path);
                f.createNewFile();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }

    public String buildAndMakeTargetDirs() throws UnknownHostException {

        DateFormat df = new SimpleDateFormat("yyMMdd_HH.mm");
        String dateString = df.format(new Date());

        String targetDir = this.targetDirRoot + dateString + "/";
        createDirs(targetDir);
        
        
       

        //createDirs(targetDir + "clientA/");
        //createDirs(targetDir + "clientB/");

        return targetDir;
    }

    /**
     * Join Appr.tc Room.
     * @param browser Browser that should join Room
     * @param room String of Room to join
     */
    public void joinSessionAppRTC(WebDriver browser, String room) {
        browser.get(AppRTC.URL_APPRTC + room);
        //browser.manage().window().maximize();
        browser.manage().window().setSize(new Dimension(1920, 1080));
        
        WebElement joinButton = browser.findElement(AppRTC.LOC_BTN_JOIN);
        if (joinButton != null) {
            joinButton.click();
        }
    }
    
    
    /**
     * Join jitsi Room.
     * @param browser Browser that should join Room
     * @param room String of Room to join
     */
    public void joinSessionJitsi(WebDriver browser, String room) {
    	browser.get(AppRTC.URL_JITSI + room);
    	//browser.manage().window().maximize();
    	browser.manage().window().setSize(new Dimension(1920, 1080));
    }

    public void createChromeRTCDump(WebDriver browser) {
        WebElement dumper = browser.findElement(AppRTC.LOC_BTN_CREATE_DUMP);
        dumper.click();
        WebElement dlBut = browser.findElement(AppRTC.LOC_BTN_DL_PEERCON);
        dlBut.click();
    }

    public void openChromeRTCInternals(WebDriver browser){

        // dirty hack to get chrome window into windows foreground
        // Only windows in foreground react to new tab (ctrl+t) sequence
        ((JavascriptExecutor)browser).executeScript("alert('Test')");
        browser.switchTo().alert().accept();
        browser.findElement(By.cssSelector("body")).sendKeys(Keys.CONTROL + "t");
        ((JavascriptExecutor)browser).executeScript("window.open()");

        if (browser.getWindowHandles().size() > 1) {
            Iterator<String> handles = browser.getWindowHandles().iterator();
            String handle = "";
            while (handles.hasNext()) {
                handle = handles.next();
            }
            browser.switchTo().window(handle);
            browser.navigate().to("chrome://webrtc-internals/");
        } else {
            throw new IllegalStateException("Second Tab in Browser " + browser.toString() + " for webrtc-internals not opened!");
        }
    }

    /**
     * Take Screenshot of Browser.
     * @param browser Source for Screenshot
     * @param targetFile TargetFile for Screenshot
     */
    public void takeScreenshot(WebDriver browser, String targetFile) {
        File scrFile = ((TakesScreenshot)browser).getScreenshotAs(OutputType.FILE);
        // Now you can do whatever you need to do with it, for example copy somewhere
        try {
            FileUtils.copyFile(scrFile, new File(targetFile));
        } catch (IOException e) {
            e.printStackTrace();
        }
    }


    /**
     * Helper Method for a pause of x seconds
     * @param seconds Wait Time in Seconds
     */
    public void pause(Integer seconds){
        try {
            TimeUnit.SECONDS.sleep(seconds);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }
    
    public ChromeDriver getChromeDriver(String targetDir, boolean test) {
    	ChromeDriver driver = new ChromeDriver(setChromeOptions(targetDir, test));
    	this.browsers.add(driver);
    	return driver;
    }


    /**
     * Helper Method to set Required ChromeOptions
     * @return Pre-setup Options for Chrome Browser
     */
    public ChromeOptions setChromeOptions(String downloadFilepath, boolean test) {
        ChromeOptions o = new ChromeOptions();
        o.addArguments("--allow-file-access-from-files"); //allows getUserMedia() to be called from file:// URLs.
        o.addArguments("disable-translate"); //disables Translate into .. Popup
        o.addArguments("use-fake-ui-for-media-stream"); //avoids the need to grant camera/microphone permissions
        o.addArguments("use-fake-device-for-media-stream"); //feeds a test pattern to getUserMedia() instead of live camera input.
        o.addArguments("use-file-for-fake-video-capture="+this.fakeFile); //feeds a Y4M test file to getUserMedia() instead of live camera input
        o.addArguments("enable-logging --v=1 --vmodule=*source*/talk/*=3"); //some logging parameters
        o.addArguments("mute-audio"); //disables sound
        
        if(!test) {
        	o.addArguments("headless");
        }
        
        //o.addArguments("disable-gpu");

        // Manage the download
        HashMap<String, Object> chromePrefs = new HashMap();
        chromePrefs.put("profile.default_content_settings.popups", 0);
        chromePrefs.put("download.default_directory", downloadFilepath);
        o.setExperimentalOption("prefs", chromePrefs);

        return o;
    }

    public Object getElementAtPositionFromList(Set<Object> list, int index) {
        int i = 0;
        for (Iterator<Object> it = list.iterator() ; it.hasNext(); i++) {
            Object o = it.next();
            if (i == index) {
                return o;
            }
        }
        return null;
    }
    
    public void cleanupBrowsers() throws Exception {
        for(WebDriver browser : this.browsers) {
            //browser.close();
            browser.quit();
        }
    }

}
