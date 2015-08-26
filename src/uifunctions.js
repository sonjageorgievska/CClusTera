 function KeyPress(e) {
            var evtobj = window.event ? event : e
            if (evtobj.keyCode == 90 && evtobj.ctrlKey) {
                if (clicked == true) {
                    RemoveLastNodes();
                    RemoveLastEdges();
                    clicked = false;                    
                    redrawSameScene();
                }           
            }
        }


 function searchSequence() {
     var value = document.getElementById("search").value;
 }


 function defineSlider() {


     mySlider.enableTooltip(true);

     mySlider.attachEvent("onChange", function () {
         var sliderval = mySlider.getValue();
         $("#label2").text(sliderval);
         if (sliderval > 0) {
             AddLevel(sliderval);
             redrawSameScene();
         }
     });

     mySlider.attachEvent("onChange", function (value) {
         updateSliderPopupValue(value);
     });

     mySlider.enable();
 };


 function defineCombo() {
     var myCombo = new dhtmlXCombo("comboObj");


     myCombo.addOption([
 ["a", "property A"],
 ["aa", "property AA"],
 ["b", "property B"],
 ["c", "property C"]
     ]);


     myCombo.attachEvent("onChange", function () {
         var comboval = myCombo.getSelectedValue();
         // $("#label2").text(comboval);
     });
     //myCombo.filter = true;
     myCombo.setSize(245);

     myCombo.enable();
 }


 function defineCombo2() {
     var myCombo2 = new dhtmlXCombo("comboObj2");


     myCombo2.addOption([
 ["a", "family"],
 ["aa", "class"],
 ["b", "type"]
     ]);


     myCombo2.attachEvent("onChange", function () {
         var comboval2 = myCombo2.getSelectedValue();
         // $("#label2").text(comboval);
     });
     //myCombo.filter = true;
     myCombo2.setSize(245);

     myCombo2.enable();
 }

 function defineColorPicker() {
     var myColorpicker = new dhtmlXColorPicker("colorpickerObj");
     myColorpicker.setCustomColors(true);
     myColorpicker.setColor("#05ff50");
     myColorpicker.setCustomColors(true);

     myColorpicker.showMemory(true);

     myColorpicker.show();

     myColorpicker.attachEvent("onSelect", function (color, node) {
         var col = myColorpicker.getSelectedColor();
         //$("#label2").text(color);
     });

     myColorpicker.attachEvent("onCancel", function (node) { });
 }

 function defineColorPicker2() {
     myColorpicker = new dhtmlXColorPicker(["inputcolor"]);
     myColorpicker.setCustomColors(true);
     myColorpicker.setColor("#05ff50");
     myColorpicker.setCustomColors(true);

     myColorpicker.showMemory(true);



     myColorpicker.attachEvent("onSelect", function (color, node) {
         var col = myColorpicker.getSelectedColor();
         //$("#label2").text(color);
     });

     myColorpicker.attachEvent("onCancel", function (node) { myColorpicker.hide() });
 }

 function updateSliderPopupValue(value) {
     myPopSlider.attachHTML("Level: " + value.toString());
 }
