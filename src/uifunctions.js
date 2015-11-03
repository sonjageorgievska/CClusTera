//functions for defining UI components and handling their events

function KeyPress(e) {//if the key combination is ctrl+z, then it will close the node that was last open. Can be called multiple times
            var evtobj = window.event ? event : e
            if (evtobj.keyCode == 90 && evtobj.ctrlKey) {////if the key combination is ctrl+z
                handleCtrlz(); 
            }
        }

 function handleCtrlz()
 {
     if (clicked > 0) {//if the user has expanded some nodes
         RemoveLastEdges();//remove the last edges that were added with clicking a node
         RemoveLastNodes();//remove the last nodes that were added with clicking a node
         lastOpenNode[clicked]._expandable = true; //when you close a node, it is expandable again
         var nodeId = lastOpenNode[clicked].getId();
         CurrentLevel[nodeId]--;//decrease the current level for the node
         var n = CurrentDir[nodeId].lastIndexOf("/");
         CurrentDir[nodeId] = CurrentDir[nodeId].substring(0, n); // go up one folder for the closed node
         clicked--;// decrease the number of clicks.
         redrawSameScene();
     }
 }


 function searchSequence() {
     var value = document.getElementById("search").value;
     SearchAndColorizeByName(value);
 }


 function defineSlider() {
     mySlider.enableTooltip(true);
     mySlider.attachEvent("onChange", function () {               
         var sliderval = mySlider.getValue();       
         fastLoadUpToLevel(sliderval);
     });
     mySlider.attachEvent("onChange", function (value) {
         updateSliderPopupValue(value);
     });
     mySlider.enable();
 };

 //function defineCombo() {
 //    var myCombo = new dhtmlXCombo("comboObj");
 //    var listOfProperties; 
 //    fetchJSONFile("data/NamesOfProperties.js", function (data) {
 //        listOfProperties = data;
 //        var len = listOfProperties.length;
 //        listOfProperties = listOfProperties.slice(0, len);
     
 //    var list = [];

 //    for (var i = 0; i < listOfProperties.length; i++)
 //    {
 //        list.push([i, listOfProperties[i]]);
 //    }


 //    myCombo.addOption(list);

    

 //    myCombo.attachEvent("onChange", function () {
 //        selectedPropertyIndex = myCombo.getSelectedValue();         
 //    });
 //    //myCombo.filter = true;
 //    myCombo.setSize(245);

 //    myCombo.enable();
 //    });
 //}

 function defineCombo() {
     var myCombo = document.getElementById("combo");
     var listOfProperties;
     fetchJSONFile("data/NamesOfProperties.js", function (data) {
         listOfProperties = data;
         var len = listOfProperties.length;
         listOfProperties = listOfProperties.slice(0, len);
         for (var i = 0; i < listOfProperties.length; i++) {
             var option = document.createElement("option");
             option.text = listOfProperties[i];
             option.value = i;
             try {
                 combo.add(option, null); //Standard 
             } catch (error) {
                 combo.add(option); // IE only
             }           
         }
     });
 }


 //function defineCombo2() {
 //    var myCombo2 = new dhtmlXCombo("comboObj2");


 ////    myCombo2.addOption([
 ////["a", "family"],
 ////["aa", "class"],
 ////["b", "type"]
 ////    ]);


 //    myCombo2.attachEvent("onChange", function () {
 //        var comboval2 = myCombo2.getSelectedValue();
         
 //        // $("#label2").text(comboval);
 //    });
 //    //myCombo.filter = true;
 //    myCombo2.setSize(245);

 //    myCombo2.enable();
 //}

 

 function defineColorPicker2() {
     myColorpicker = new dhtmlXColorPicker(["inputcolor"]);
     myColorpicker.setCustomColors(true);
     myColorpicker.setColor("#05ff50");
     myColorpicker.setCustomColors(true);

     myColorpicker.showMemory(true);



     myColorpicker.attachEvent("onSelect", function (color, node) {
         var col = myColorpicker.getSelectedColor();
         var myCombo = document.getElementById("combo");
         var selectedPropertyIndex = myCombo.options[myCombo.selectedIndex].value;

         Colorize(col, selectedPropertyIndex);
         //$("#label2").text(color);
     });

     myColorpicker.attachEvent("onCancel", function (node) { myColorpicker.hide() });
 }

 function updateSliderPopupValue(value) {
     myPopSlider.attachHTML("Level: " + value.toString());
 }
