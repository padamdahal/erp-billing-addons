openerp.web_nepali_datepicker = function(instance) {
var _t = instance.web._t;
var QWeb = instance.web.qweb;

var lang = 'en';

instance.web.DateTimeWidget.include({
    start: function() {
        this.$input = this.$el.find('input.oe_datepicker_master');
        this.$input_picker = this.$el.find('input.oe_datepicker_container');
        this.$input_nepali = this.$el.find('input.oe_nepali');
        this.$parent = this.$el.parents().find('.filters-menu').parent();
        $(this.$input_nepali).val('');
        this._super();
        this.$input = this.$el.find('input.oe_simple_date');
        this.$input_nepali = this.$el.find('input.oe_nepali');
		var self = this;
		//var lang = this.options.language;

        $('.oe_nepali').calendarsPicker({
         	calendar: $.calendars.instance('nepali',lang),
         	dateFormat: 'dd/mm/yyyy',
         	onSelect: function(date){
         		if (date.length == 0) {
                	self.$el.find('input.oe_simple_date').val('');
                	self.change_datetime();
                    return false
                }
                var jd = $.calendars.instance('nepali').toJD(parseInt(date[0].year()),parseInt(date[0].month()),parseInt(date[0].day()));
                var date = $.calendars.instance('gregorian').fromJD(jd);
                var date_value = new Date(parseInt(date.year()),parseInt(date.month())-1,parseInt(date.day()));
                self.$el.find('input.oe_simple_date').val(self.format_client(date_value));
                self.change_datetime();
         	},
     	});
    },
    on_picker_select: function(text, instance) {
		this._super(text, instance);    	
        this.convert_gregorian_nepali(text);
    },
    convert_gregorian_nepali: function(text) {
        if (text) {
			calendar = $.calendars.instance('gregorian');
			calendar1 = $.calendars.instance('nepali');
        	if (text.indexOf('-')!= -1){
        		text_split = text.split('-');
        		year = parseInt(text_split[0]);
        		month = parseInt(text_split[1]);
        		day = parseInt(text_split[2]);			
							
        		var jd = calendar.toJD(year,month,day);
            	var date = calendar1.fromJD(jd);
				m = (date.month() >=10 ? date.month():"0"+date.month());
        		d = (date.day() >=10 ? date.day():"0"+date.day());         
        		$(this.$input_nepali).val(calendar1.formatDate('dd/mm/yyyy', date));
        	}
        	
        	if(text.indexOf('/')!= -1){            		
        		text_split = text.split('/');
        		year = parseInt(text_split[2]);
        		month = parseInt(text_split[0]);
        		day = parseInt(text_split[1]);			
        		var jd = calendar.toJD(year,month,day);
            	var date = calendar1.fromJD(jd);                	
				m = (date.month() >=10 ? date.month():"0"+date.month());
        		d = (date.day() >=10 ? date.day():"0"+date.day());         
        		$(this.$input_nepali).val(calendar1.formatDate('dd/mm/yyyy', date));
        	}
        	
        }
    },
    
    set_value: function(value) {
        this._super(value);
        $(this.$input_nepali).val('');
        this.convert_gregorian_nepali(value);
        this.$input.val((value) ? this.format_client(value) : '');
    },
    set_value_from_ui: function() {
        this._super();
        var value = this.$input.val() || false;
        this.value = this.parse_client(value);
        this.convert_gregorian_nepali(this.value);
    },
    set_readonly: function(readonly) {
        this._super(readonly);
        this.$input_nepali.prop('readonly', this.readonly);
    },
	change_datetime: function(e) {
	    if(this.is_valid_()) {
            this.set_value_from_ui_();
            this.trigger("datetime_changed");
        }       
	},
});

instance.web.form.FieldDatetime.include({
    initialize_content: function() {
        if (!this.get("effective_readonly")) {
            this.datewidget = this.build_widget();
            this.datewidget.on('datetime_changed', this, _.bind(function() {
                this.internal_set_value(this.datewidget.get_value());
            }, this));
            this.datewidget.appendTo(this.$el.find(".oe_simple_date")[0]);
            this.setupFocus(this.datewidget.$input);
            this.format = "%m/%d/%Y";
            var showtime = false;
            this.calendar_format = this.field.type;

            this.datewidget.calendar_format = this.field.type;
            if (this.field.type == 'datetime'){
                this.format = "%m/%d/%Y %H:%M:%S"
                showtime = true
            }
            var self = this;
           
            $('.oe_nepali').calendarsPicker({
            	calendar: $.calendars.instance('nepali',lang),
            	dateFormat: 'dd/mm/yyyy',
            	onSelect: function(date){
             		if (date.length == 0) {
                    	self.$el.find('input.oe_simple_date').val('');
                    	self.change_datetime();
                        return false
                    }
                    var jd = $.calendars.instance('nepali').toJD(parseInt(date[0].year()),parseInt(date[0].month()),parseInt(date[0].day()));
                    var date = $.calendars.instance('gregorian').fromJD(jd);
                    var date_value = new Date(parseInt(date.year()),parseInt(date.month())-1,parseInt(date.day()));
                    self.$el.find('input.oe_simple_date').val(self.format_client(date_value));
                    self.change_datetime();
             	},
        	});
        }
        this.calendar_format = this.field.type;
    },
    convert_gregorian_nepali: function(text) {
    	if (text) {
        	if (text.indexOf('-')!= -1){
        		var text_split = text.split('-');
        		var year = parseInt(text_split[0]);
        		var month = parseInt(text_split[1]);
        		var day = parseInt(text_split[2]);
        		var calendar = $.calendars.instance('gregorian');
    	        var calendar1 = $.calendars.instance('nepali');
        		var jd = $.calendars.instance('gregorian').toJD(year,month,day);
            	var date = $.calendars.instance('nepali').fromJD(jd);
        	}
        	if(text.indexOf('/')!= -1){
        		var text_split = text.split('/');
        		var year = parseInt(text_split[2]);
        		var month = parseInt(text_split[0]);
        		var day = parseInt(text_split[1]);
        		var calendar = $.calendars.instance('gregorian');
                var calendar1 = $.calendars.instance('nepali');	
        		var jd = calendar.toJD(year,month,day);
            	var date = calendar1.fromJD(jd);
        	}
        	return (calendar1.formatDate('dd/mm/yyyy', date));
        }
        return '';
    },
    render_value: function() {
    	if (!this.get("effective_readonly")) {
            this.datewidget.set_value(this.get('value'));
        } else {
            var date_value = instance.web.format_value(this.get('value'), this, '');
            this.$el.find(".oe_simple_date").text(date_value);
            this.$el.find(".oe_nepali_date").text(this.convert_gregorian_nepali(this.get('value')));
        }
    },
    is_syntax_valid: function() {
        if (!this.get("effective_readonly") && this.datewidget) {
            return this.datewidget.is_valid_();
        }
        return true;
    },
    is_false: function() {
        return this.get('value') === '' || this._super();
    },
    focus: function() {
        var input = this.datewidget && this.datewidget.$input[0];
        return input ? input.focus() : false;
    },
    set_dimensions: function (height, width) {
        this._super(height, width);
        if (!this.get("effective_readonly")) {
            this.datewidget.$input.css('height', height);
        }
    }
});
};
