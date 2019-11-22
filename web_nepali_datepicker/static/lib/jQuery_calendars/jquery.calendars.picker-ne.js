(function($) {
	$.calendarsPicker.regionalOptions['ne'] = {
		renderer: $.calendarsPicker.defaultRenderer,
		prevText: 'अघिल्लो पाठ', prevStatus: 'अघिल्लो स्थिति',
		prevJumpText: 'अघिल्लो कूदपाठ', prevJumpStatus: '',
		nextText: 'अर्को पाठ', nextStatus: 'अर्को स्थिति',
		nextJumpText: 'अर्को कूदपाठ', nextJumpStatus: '',
		currentText: 'हालको पाठ', currentStatus: 'वर्तमान स्थिति',
		todayText: 'आजपाठ', todayStatus: 'आज स्थिति',
		clearText: 'पाठखाली गर्नुहोस्', clearStatus: 'खाली गर्नुहोस्',
		closeText: 'बन्दपाठ', closeStatus: 'बन्द गर्नुहोस्',
		yearStatus: 'वर्ष स्थिति', monthStatus: 'महिना को स्थिति',
		weekText: 'हप्ताको पाठ', weekStatus: 'हप्ताको स्थिति',
		dayStatus: 'चयन D, M d', defaultStatus: 'पूर्वनिर्धारितस्थिति',
		isRTL: false
	};
	$.calendarsPicker.setDefaults($.calendarsPicker.regionalOptions['ne']);
})(jQuery);
