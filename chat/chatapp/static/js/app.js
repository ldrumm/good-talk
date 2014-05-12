var chatmain = function(){
    

//    var escapeHTML = function(str) { return str.replace(/([&<>])/g,function (c) {return "&" + {"&": "amp","<": "lt",">": "gt"}[c] + ";";}   ); };
    var escapeHTML = function(s){return s;};    
    var self = {};
    
    self.display = $('#chatwindow');
    console.log(self.display);
    self.input = $('#chatinput');
    self.retry_delay = 0; //used for backoff after request failure
    
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
    
    self.displaymessage = function(msg, user){
        if(!user){
            user = '';
        }
        if(msg == null){
            return ;
        }
        self.display.append('<p><strong>' + escapeHTML(user) + ':</strong>' + escapeHTML(msg)+ '</p>');
    };
    self.submit = function(msg){
        console.log('submitting' + msg);
        $.ajax({
    			    type: "POST",
                    data: {request:
                        JSON.stringify({
                            cmd:'submit',
                            data:msg,
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
			     }
			 );
	};
	self.failure = function(callback) {
	    self.retry_delay = ((self.retry_delay < 1) ? 1 : (self.retry_delay * 2 > 60) ? 60 : self.retry_delay * 2);
	    console.log('request failed; backoff is now ' + self.retry_delay);
	    window.setTimeout(callback, self.retry_delay * 1000);
	};
	self.success = function(callback) {
	    self.retry_delay = 0;
	    console.log('request succeeded; backoff is now ' + self.retry_delay);
	    window.setTimeout(callback, self.retry_delay * 1000);
	}
    self.waitupdate = function(){
        console.log('waitupdate');
        $.ajax({
    			    type: "POST",
                    data: {request:
                        JSON.stringify({
                            cmd:'update',
                            timeout:'30000'
                        })
                    },
			        dataType: 'json'}
            ).done(function(data, textStatus, jqXHR){
                        console.log(data);
			            self.displaymessage(data.msg);
			            if(data.success||data.timeout){
    			            self.success(self.waitupdate);
    			         }
            }).fail(function(){
                self.failure(self.waitupdate);
            });
    };
    self.main = function(){
        self.waitupdate();
    
    };
    self.main();
    return self;
}
