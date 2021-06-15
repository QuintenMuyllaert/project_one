document.addEventListener("DOMContentLoaded",async () => {
    const data = await fetchJson("/data.json");
    const slider = document.getElementById("slider");
    slider.value = data.bright;
    slider.addEventListener("change",function(){
        socket.emit("brightness",slider.value);
    })

    document.getElementById("hamburger").addEventListener("click",function(){
        console.log("Clicked hamburger menu.");
        document.getElementById("hamburger-menu").classList["add"]("shown");
    });

    document.addEventListener("click",function(e){
        try{
            if(!(e.target.parentNode.id.includes("hamburger"))){
                document.getElementById("hamburger-menu").classList["remove"]("shown");
            }
        }catch(err){};//anti crash, incase body geklikt is.
    })

    const effectPicker = document.getElementById("effects"); 
    effectPicker.addEventListener("change",function(){
        console.log("Swap to",this.value)
        socket.emit("setEffect",this.value);
        updateHtml();
    })
    effectPicker.value = data.effect;

    document.getElementById("hamburger-list").children.forEach(elem => {
        elem.addEventListener("click",function(){
            console.log("Go to",this.innerHTML);
            document.querySelector("main").children.forEach(elem => {
                if(this.innerHTML.toLowerCase() == elem.id){
                    elem.classList.remove("hidden");
                }else{
                    elem.classList.add("hidden");
                }
            });
            hamShown = false;
            document.getElementById("hamburger-menu").classList["remove"]("shown");
        })
    });

    setInterval(() => {
        socket.emit("dht",1);
    }, 1000);

    updateHtml();
    document.getElementById("loadingscreen").style.opacity = 0;
    document.getElementById("main").classList.remove("hidden");
    document.getElementById("navigation").classList.remove("hidden");
    setTimeout(() => {
        document.getElementById("loadingscreen").classList.add("hidden");    
    }, 1000);
    
    console.log("Finished loading!");
});

function updateHtml(){
    const effectHtml = document.getElementById("effects");
    const selectedEffect = effectHtml.value;
    for(const child of effectHtml){
        const effect = child.value;
        const effectNameHtml = document.getElementById(`effect-${effect}`);
        if(effectNameHtml){
            if(selectedEffect == effect){
                effectNameHtml.classList.remove("hidden");
            }else{
                effectNameHtml.classList.add("hidden");
            }
        }
    }   
}

//socket.io.js calls
const socket = io();
socket.on('connect', function () {
    console.log("connected");
    const date = new Date(Date.now());
    const months = ["JAN","FEB","MRT","APR","MAY","JUN","JUL","AUG","SEP","OKT","NOV","DEC"];
    const time_calibration = `${date.getDate()} ${months[date.getUTCMonth()]} ${date.getUTCFullYear()} ${date.getUTCHours()}:${date.getUTCMinutes()}:${date.getUTCSeconds()}`;
    socket.emit('time', time_calibration);
});

socket.on("weather",function(val){
    const tempHtml = document.getElementById("temperature");
    const humiHtml = document.getElementById("humidity");
    
    tempHtml.innerHTML = `${Math.round(val.temp*10)/10}°C`
    humiHtml.innerHTML = `${val.humi}%`;
});

socket.on("brightness",function(val){
    document.getElementById("slider").value = val;
});

socket.on("setEffect",function(effect){
    console.log("External swap to",effect)
    document.getElementById("effects").value = effect;
    updateHtml();
})

//P5.js for solid mode
const s = ( p ) => {
    function minMax(val,mini,maxi){
        return val < mini ? false : val > maxi ? false : true;
    }

    p.setup = function() {
        this.noStroke();
        this.createCanvas(255, 255);
    };

    p.draw = function() {
        p.colorMode(p.HSB,255);
        this.background(0,0,255);
        for(let x = 0;x<255;x++){
            for(let y = 0;y<255;y++){
                p.fill(x,y,255);
                p.rect(255-x,y,1,1);
            }    
        }
        p.noLoop();
    };

    p.touchStarted = function() {
        if(minMax(p.mouseX,0,p.width) && minMax(p.mouseY,0,p.height)){
            console.log(p.mouseX,p.mouseY);
            socket.emit("solid",{h:p.mouseX,s:p.mouseY});
        }
    }
};


let myp5 = new p5(s,"p5-container");

//amcharts.js
am4core.ready(async function() {
    const names = [
        "Sunday",
        "Monday",
        "Thuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Satterday"
    ];
    let high = [0,1,2,3,4,5,6];
    let low = [-1,-2,-3,-4,-5,-6,-7];

    const now = new Date(Date.now());
    
    now.setUTCHours(0);
    now.setUTCMinutes(0);
    now.setUTCSeconds(0);
    now.setUTCMilliseconds(0);
    
    const vals = await fetchJson(`./history.json`);
    console.log(vals);
    let order = []
    for(let i in vals.time){
        order.push(names[new Date(vals.time[i]).getDay()])
    }

    makeChart("chartdiv",order,vals.tmp_h,vals.tmp_l,"Hi/Low: {openValueY.value}°C / {valueY.value}°C");
    makeChart("chartdiv2",order,vals.dht_h,vals.dht_l,"Hi/Low: {openValueY.value}% / {valueY.value}%");
});


function makeChart(div,labels,high,low,tooltip){
    //very ugly code from amcharts example page.
    am4core.useTheme(am4themes_animated);

    let chart = am4core.create(div, am4charts.XYChart);

    let data = [];

    for (let i = 0; i < labels.length; i++) {
        data.push({ category: labels[i], open: high[i], close: low[i] });
    }

    chart.data = data;
    let categoryAxis = chart.xAxes.push(new am4charts.CategoryAxis());
    categoryAxis.renderer.grid.template.location = 0;
    categoryAxis.dataFields.category = "category";
    categoryAxis.renderer.minGridDistance = 15;
    categoryAxis.renderer.grid.template.location = 0.5;
    categoryAxis.renderer.grid.template.strokeDasharray = "1,3";
    categoryAxis.renderer.labels.template.rotation = -90;
    categoryAxis.renderer.labels.template.horizontalCenter = "left";
    categoryAxis.renderer.labels.template.location = 0.5;
    categoryAxis.renderer.inside = true;

    categoryAxis.renderer.labels.template.adapter.add("dx", function(dx, target) {
        return -target.maxRight / 2;
    })

    let valueAxis = chart.yAxes.push(new am4charts.ValueAxis());
    valueAxis.tooltip.disabled = true;
    valueAxis.renderer.ticks.template.disabled = true;
    valueAxis.renderer.axisFills.template.disabled = true;

    let series = chart.series.push(new am4charts.ColumnSeries());
    series.dataFields.categoryX = "category";
    series.dataFields.openValueY = "open";
    series.dataFields.valueY = "close";
    series.tooltipText = tooltip;
    series.sequencedInterpolation = true;
    series.fillOpacity = 0;
    series.strokeOpacity = 1;
    series.columns.template.width = 0.01;
    series.tooltip.pointerOrientation = "horizontal";

    let openBullet = series.bullets.create(am4charts.CircleBullet);
    openBullet.locationY = 1;

    let closeBullet = series.bullets.create(am4charts.CircleBullet);

    closeBullet.fill = chart.colors.getIndex(4);
    closeBullet.stroke = closeBullet.fill;

    chart.cursor = new am4charts.XYCursor();
}