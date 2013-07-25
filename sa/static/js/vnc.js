var INCLUDE_URI = "/static/novnc/";

Util.load_scripts(["webutil.js", "base64.js", "websock.js", "des.js",
                   "input.js", "display.js", "jsunzip.js", "rfb.js"]);

function updateVNCState(rfb, state, oldstate, msg) {
    var s, sb, cad, klass;
    s = $D('VNC_status');
    sb = $D('VNC_status_bar');
    cad = $D('sendCtrlAltDelButton');
    switch (state) {
    case 'failed':
    case 'fatal':
        klass = "VNC_status_error";
        break;
    case 'normal':
        klass = "VNC_status_normal";
        break;
    case 'disconnected':
    case 'loaded':
        klass = "VNC_status_normal";
        break;
    case 'password':
        klass = "VNC_status_warn";
        break;
    default:
        klass = "VNC_status_warn";
    }

    if (state === "normal") { cad.disabled = false; }
    else                    { cad.disabled = true; }

    if (typeof(msg) !== 'undefined') {
        sb.setAttribute("class", klass);
        s.innerHTML = msg;
    }
}

//setups VNC application
function setupVNC(){

    //Append to DOM
    dialogs_context = $("body");
    dialogs_context.append('<div id="vnc_dialog" title="VNC connection"></div>');
    $vnc_dialog = $('#vnc_dialog',dialogs_context);
    var dialog = $vnc_dialog;

    dialog.html('\
      <div id="VNC_status_bar" class="VNC_status_bar" style="margin-top: 0px;">\
         <table border=0 width="100%"><tr>\
            <td><div id="VNC_status">Loading</div></td>\
            <td width="1%"><div id="VNC_buttons">\
            <input class="btn" type=button value="Send CtrlAltDel"\
                   id="sendCtrlAltDelButton">\
            </div></td>\
          </tr></table>\
        </div>\
        <canvas id="VNC_canvas" width="640px" height="20px">\
            Canvas not supported.\
        </canvas>\
');

    dialog.dialog({
        autoOpen:false,
        width:829,
        modal:true,
        height:695,
        resizable:true,
        closeOnEscape: false
    });

    $('#sendCtrlAltDelButton',dialog).click(function(){
        rfb.sendCtrlAltDel();
        return false;
    });

    dialog.bind( "dialogclose", function(event, ui) {
        rfb.disconnect();
    });

    $("a[href='#vnc']").click(function(){
        //Which VM is it?
         var id = $(this).attr('data-sid');
        //Ask server for connection params
        $.ajax({
            type: "POST",
            url: "/server/"+ id +"/startvnc",
            dataType: "json",
            async: false,
            success: function(data){
                vncCallback(null, data);
            }
        });

        return false;
    });
}

function vncCallback(request,response){
    rfb = new RFB({'target':       $D('VNC_canvas'),
                   'encrypt':      false,
                   'true_color':   true,
                   'local_cursor': true,
                   'shared':       true,
                   'updateState':  updateVNCState});

    var proxy_host = 'apc10-001.i.ajkdns.com';
    var proxy_port = 33876;
    var pw = response["password"];
    var token = response["token"];
    var path = '?token='+token;
    rfb.connect(proxy_host, proxy_port, pw, path);
    $vnc_dialog.dialog('open');
}

function vncIcon(vm){
    var gr_icon;
    if (vnc_enable){
        gr_icon = '<a class="vnc" href="#" vm_id="'+vm.ID+'">';
        gr_icon += '<img src="images/vnc_on.png" alt=\"'+tr("Open VNC Session")+'\" /></a>';
    }
    else {
        gr_icon = '<img src="images/vnc_off.png" alt=\"'+tr("VNC Disabled")+'\" />';
    }
    return gr_icon;
}
