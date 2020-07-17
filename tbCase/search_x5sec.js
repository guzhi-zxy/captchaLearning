const puppeteer = require('puppeteer');

async function openBrowser() {
    let browser_settings = {};

    args = ['--disable-infobars', '--no-sandbox', '--disable-setuid-sandbox', '--password-store=basic', '--account-consistency', '--aggressive', '--allow-running-insecure-content', '--allow-no-sandbox-job', '--allow-outdated-plugins', '--disable-gpu'];
    browser_settings["args"] = args;
    browser_settings["headless"] = false;
    browser_settings["ignoreDefaultArgs"] = ["--enable-automation"];
    browser_settings["defaultViewport"] = {width:1366, height: 768};

    browser = await puppeteer.launch(browser_settings);
    console.log("open browser success!");
    return browser
}

// 反检测
async function initPage(page) {
    await page.evaluateOnNewDocument(() => {
        // Set webdriver false
        Object.defineProperty(navigator, 'webdriver', {
            get: () => false,
        });
    }).catch(err => {
        console.log(err)
    });

    await page.evaluateOnNewDocument(() => {
        // We can mock this in as much depth as we need for the test.
        window.navigator.chrome = {
            runtime: {},
            // etc.
        };
    }).catch(err => {
        console.log(err)
    });

    await page.evaluateOnNewDocument(() => {
        // Pass the Chrome Test.
        Object.defineProperty(navigator, 'languages', {
            get: function () {
                return ["zh-CN", "zh", "en", "zh-TW", "fr", "pt", "pl"];
            },
        });
    }).catch(err => {
        console.log(err)
    });

    await page.evaluateOnNewDocument(() => {
        // Overwrite the `plugins` property to use a custom getter.
        Object.defineProperty(navigator, 'plugins', {
            // This just needs to have `length > 0` for the current test,
            // but we could mock the plugins too if necessary.
            get: () => [1, 2, 3, 4, 5],
        });
    }).catch(err => {
        console.log(err)
    });

    await page.evaluateOnNewDocument(() => {
        const getParameter = WebGLRenderingContext.getParameter;
        WebGLRenderingContext.prototype.getParameter = function (parameter) {
            // UNMASKED_VENDOR_WEBGL
            if (parameter === 37445) {
                return 'Intel Open Source Technology Center';
            }
            // UNMASKED_RENDERER_WEBGL
            if (parameter === 37446) {
                return 'Mesa DRI Intel(R) Ivybridge Mobile ';
            }

            return getParameter(parameter);
        };
    }).catch(err => {
        console.log(err)
    });

    await page.evaluateOnNewDocument(() => {
        // Pass the Permissions Test.
        const originalQuery = window.navigator.permissions.query;
        return window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({state: Notification.permission}) :
                originalQuery(parameters)
        );
    }).catch(err => {
        console.log(err)
    });

    console.log('Init page success.');
    return page
}


async function main(url) {
    const brower = await openBrowser();
    const page = await brower.newPage();
    await page.setUserAgent('Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1');
     await page.setViewport({
       width: 375,
       height: 812,
       isMobile: true
     });
    await initPage(page);
    await page.goto(url);
    console.log('starting....');
    // await page.tap('#nc_1_n1z');
    await page.tap('#nc_1_n1t');
    const text = await page.evaluate(() => {

        event = document.createEvent('MouseEvents');

        event.initEvent('mousedown', true, false);
        document.querySelector("#nc_1_n1t").dispatchEvent(event);
        event = document.createEvent('MouseEvents');
        event.initEvent('mousemove', true, false);
        Object.defineProperty(event,'clientX',{get(){return 258}});
        document.querySelector("#nc_1_n1t").dispatchEvent(event);
        // document.querySelector("#nc_1_n1z").dispatchEvent(event);
        // console.log("cookie :" + document.cookie);

    });
    await page.waitFor(2000);
    // var cookies = await page._client.send('Network.getAllCookies');
    let cookies = await page.evaluate(() => document.cookie);
    // const cookies = await page.cookies('https://s.taobao.com/');
    console.log(cookies);


    console.log('click done !!!');


}

main("https://s.taobao.com:443//search/_____tmd_____/punish?x5secdata=5e0c8e1365474455070961b803bd560607b52cabf5960afff39b64ce58073f78f68ede033dd239842063c29628191423773f1e4d712042da0b04859e7922f0cd1cb5a8128717e0f3420b48c6ecc334025a28f087d8bad4d6fd186fb500b0ba0345cb0ce36cef9f62cbd52852a03cf8ba461ee819ca12264cfd380e1ff9a3181717201d901aba50ddfb20f0b000b338b4809d51816da1a7d44dba03fc0243f03122d63a58b4646145d9027705ca5182edda92297ed56a297b527fabd4fb0db2aa5fd102e32437f7b8741ec5aa54e4ecf0cfc7fb60384b6e7cea2b1e6ed607028e3580eaf5597472011e5d935de5479673ccce14433bb614a9a5a1ea733f3f3ca3be64fe7c2b8f69454c3030f98912b20e29800710b25af63e0b6e347d120acba5f9b86c27692bf843654469bc1ede3d7d30112493051f83559dad5226f20be1b7fe3d96f437e26cb843d9bd96ae725188f8b26098ae3913dec42886212a6d7a39261b7f764385dfac9875f00815d4a5d1fc15226eeb0f8111cb7facd8c2da18d4e1a1ccc161f12b55f52eb945ca25803b1316fb769c34ded91d724c67bb14fab0cc8547825ddaf593c1d5ddedce4c8381dda07e84c344afeb62324a8762edc3c3ac3a574be463b6e88aea82bb32ce0a9f4afed865b37df553413632bda117659990bc02239293e5b8d5f4eb38285ce7c29385cda20b2885e1ec2ac43f672ace63&x5step=2");