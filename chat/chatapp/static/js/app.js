var chatmain = function(chatWindowEl, chatInputEl, keyEl, roomEl, aliasEl){
    var JsonFormatter = {
        stringify: function (cipherParams) {
            var jsonObj = {
                ciphertext: cipherParams.ciphertext.toString(CryptoJS.enc.Base64)
            };
            if (cipherParams.iv) {
                jsonObj.iv = cipherParams.iv.toString();
            }
            if (cipherParams.salt) {
                jsonObj.salt = cipherParams.salt.toString();
            }
            return jsonObj;
        },
        parse: function (jsonObj) {
            var cipherParams = CryptoJS.lib.CipherParams.create({
                ciphertext: CryptoJS.enc.Base64.parse(jsonObj.ciphertext)
            });
            if (jsonObj.iv) {
                cipherParams.iv = CryptoJS.enc.Hex.parse(jsonObj.iv)
            }
            if (jsonObj.salt) {
                cipherParams.salt = CryptoJS.enc.Hex.parse(jsonObj.salt)
            }
            return cipherParams;
        }
    };
    var escapeHTML = function(str) { 
        return str.replace(
            /([&<>])/g, 
            function (c){
                return "&" + {"&": "amp","<": "lt",">": "gt"}[c] + ";";
            }
        ); 
    };
    var self = {};
    var key;
    self.display = $(chatWindowEl);
    self.input = $(chatInputEl);
    self.roomName = $(roomEl).val();
    self.roomName = "hut2";
    key = $(keyEl).val();
    key = "password";
    self.alias = $(aliasEl).val();
    self.alias = 'Dragon';
    
    self.backOff = 0; //used for backoff after request failure
    self.timeout = 5;
    self.crypt = function(plaintext){
        /*Takes an abitrary plaintext and encrypts it.  
        Returns an object with 'ciphertext', 'iv' and 'salt' indexes suitable 
        for decryption with self.decrypt()
        */
        var crypt = CryptoJS.AES.encrypt(self.alias + ':' + plaintext, key);
        console.log();
        return JsonFormatter.stringify(crypt);
    };
    
    self.decrypt = function(msg){
        //given an object with with 'ciphertext', 'iv' and 'salt' indexes its plaintext
        if(key == null){
            alert("Please enter your secret passphrase");
        }
        else{
            var crypto = JsonFormatter.parse(msg);
            var plaintext = CryptoJS.AES.decrypt(
                crypto, 
                key,
                {iv:crypto.iv, salt:crypto.salt}
            );
            plaintext = CryptoJS.enc.Utf8.stringify(plaintext);
            if (plaintext.toString().length == 0){
                return null;
            }
                
            return {
                alias:plaintext.split(':')[0],
                text:plaintext.slice(plaintext.indexOf(':') + 1)
            };
        }
    };

    self.input.keyup(function(event){
        if(event.which == 13 && !event.shiftKey){
            var text = self.input.val();
            if(text.length){
                self.submit(text);
                self.input.val('');
            }
            event.preventDefault();
        }
    });
    
    self.displayMessage = function(msg){
        if(msg != null){
            var msg = self.decrypt(msg);
            if(msg === null){
                self.display.append('<p>*received undecodable message*</p>');
            }else
                self.display.append('<p><strong>' + escapeHTML(msg.alias) + ':</strong>' + escapeHTML(msg.text) + '</p>');
        }
            
    };

    self.submit = function(msg){
        $.ajax({
		    type: "POST",
            data: {request:
                JSON.stringify({
                    command:'submit',
                    subscriber:self.roomName,
                    data:self.crypt(msg),
                    timeout:self.timeout,
                })
            },
	        dataType: 'json'}
		).done(function(data, textStatus, jqXHR){
            if(!data.success){
                alert('failed to send message');
            }
            else{
                self.success(function(){});
            }
	   });
	};
	
	self.failure = function(callback) {
	    /*Exponential backoff in case the network is down*/
	    self.backOff = ((self.backOff < 1) ? 1 : (self.backOff * 2 > 60) ? 60 : self.backOff * 2);
	    console.log('request failed; backoff is now ' + self.backOff);
	    window.setTimeout(callback, self.backOff * 1000);
	};
	
	self.success = function(callback) {
	    if(self.backOff != 0){
	        self.backOff = 0;   //revoke any exponential backoff
	        console.log('request succeeded; backoff is now ' + self.backOff);
	    }
	    window.setTimeout(callback, self.backOff * 1000);
	}
	
    self.waitUpdate = function(){
        console.log('waitUpdate');
        $.ajax({
		    type: "POST",
            data: {
                request: JSON.stringify({
                    subscriber:self.roomName,
                    command:'update',
                    timeout:self.timeout
                })
            },
	        dataType: 'json'
	   }).done(function(response, textStatus, jqXHR){
            console.log(response);
            self.displayMessage(response.data);
            if(response.success||response.timeout){
	            self.success(self.waitUpdate);
	         }
        }).fail(function(){
            self.failure(self.waitUpdate);
        });
    };
    self.main = function(){
        self.waitUpdate();
    };
    self.main();
    return self;
}
