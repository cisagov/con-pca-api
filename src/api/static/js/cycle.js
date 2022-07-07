function createClickRateOverTime() {
  var ctx = document.getElementById("click-rate-over-time").getContext("2d");
  var currentCycle = JSON.parse(
    document.getElementById("currentCycle").innerText
  );
  var previousCycles = JSON.parse(
    document.getElementById("previousCycles").innerText
  );

  var labels = ["Low (1, 2)", "Moderate (3, 4)", "High (5, 6)"];
  var datasets = [
    {
      data: [
        Math.round(currentCycle.stats.stats.low.clicked.ratio * 100),
        Math.round(currentCycle.stats.stats.moderate.clicked.ratio * 100),
        Math.round(currentCycle.stats.stats.high.clicked.ratio * 100),
      ],
      label: `Report Cycle`,
      backgroundColor: "#064875",
    },
  ];

  var colors = ["#fcbf10", "#007bc1"];

  if (previousCycles.length > 0) {
    for (var i = 0; i < previousCycles.length; i++) {
      if (i < 2) {
        datasets.push({
          data: [
            Math.round(previousCycles[i].stats.stats.low.clicked.ratio * 100),
            Math.round(
              previousCycles[i].stats.stats.moderate.clicked.ratio * 100
            ),
            Math.round(previousCycles[i].stats.stats.high.clicked.ratio * 100),
          ],
          label: `Cycle #${i + 2}`,
          backgroundColor: colors[i],
        });
      }
    }
  }

  const data = {
    labels: labels,
    datasets: datasets.reverse(),
  };

  const options = {
    plugins: {
      legend: {
        display: true,
        position: "right",
      },
      datalabels: {
        color: "white",
        font: {
          weight: "bold",
        },
        display: function (context) {
          return context.dataset.data[context.dataIndex] > 0;
        },
        formatter: function (value, ctx) {
          return value + "%";
        },
      },
    },
    scales: {
      y: {
        ticks: {
          maxTicksLimit: 4,
        },
      },
    },
  };

  const chart = new Chart(ctx, {
    type: "bar",
    data: data,
    options: options,
    plugins: [ChartDataLabels],
  });
}

function getClickRateFromCycle(cycle, level) {
  return Math.round(cycle.stats.stats[level].clicked.ratio * 100);
}

function clickRateTimeIntervalChart() {
  var ctx = document
    .getElementById("click-rate-time-interval")
    .getContext("2d");
  const timeStats = JSON.parse(
    document.getElementById("timeIntervalStats").innerText
  );
  const clicked = timeStats.clicked;
  const data = {
    labels: [
      "1 minute",
      "3 minutes",
      "5 minutes",
      "15 minutes",
      "30 minutes",
      "60 minutes",
      "2 hours",
      "3 hours",
      "4 hours",
      "1 day",
    ],
    datasets: [
      {
        data: [
          clicked.one_minutes.ratio * 100,
          clicked.three_minutes.ratio * 100,
          clicked.five_minutes.ratio * 100,
          clicked.fifteen_minutes.ratio * 100,
          clicked.thirty_minutes.ratio * 100,
          clicked.sixty_minutes.ratio * 100,
          clicked.two_hours.ratio * 100,
          clicked.three_hours.ratio * 100,
          clicked.four_hours.ratio * 100,
          clicked.one_day.ratio * 100,
        ],
        backgroundColor: "#164a91",
        label: "Clicked Percentage",
      },
    ],
  };

  const options = {
    plugins: {
      legend: {
        display: false,
        position: "top",
      },
      datalabels: {
        anchor: "end",
        align: "top",
        color: "black",
        font: {
          weight: "bold",
        },
        display: function (context) {
          return context.dataset.data[context.dataIndex] > 0;
        },
        formatter: function (value, ctx) {
          return value + "%";
        },
      },
    },
    layout: {
      padding: {
        top: 20,
      },
    },
    scales: {
      y: {
        min: 0,
        max: 100,
        ticks: {
          count: 6,
        },
        title: {
          display: true,
          text: "% of Unique User Clicks",
        },
      },
      x: {
        title: {
          display: true,
          text: "Time Intervals",
        },
      },
    },
  };

  new Chart(ctx, {
    type: "bar",
    data: data,
    options: options,
    plugins: [ChartDataLabels],
  });
}

function millisecondToTextDate() {
  var currentCycle = JSON.parse(
    document.getElementById("currentCycle").innerText
  );

  var remainingMills = currentCycle.stats.stats.all.clicked.median;
  var days = 0;
  var hours = 0;
  var minutes = 0;
  var seconds = 0;

  var retVal = "The median time to click was ";
  if (remainingMills == 0) {
    retVal += "not found";
  }

  //days
  if (remainingMills > 86400000) {
    days = Math.floor(remainingMills / 86400000);
    retVal += days + " days" + (remainingMills > 3600000 ? ", " : ".");
    remainingMills = remainingMills % 86400000;
  }
  //hours
  if (remainingMills > 3600000) {
    hours = Math.floor(remainingMills / 3600000);
    retVal += hours + " hours" + (remainingMills > 60000 ? ", " : ".");
    remainingMills = remainingMills % 3600000;
  }
  //minutes
  if (remainingMills > 60000) {
    minutes = Math.floor(remainingMills / 60000);
    remainingMills = remainingMills % 60000;
    retVal += minutes + " minutes" + (remainingMills > 1000 ? ", " : ".");
  }
  //seconds
  if(remainingMills > 1000 ){
    seconds = Math.floor(remainingMills / 1000) ;
    retVal += (seconds + " seconds.")
  }
  document.getElementById("timeIntervalClickInText").textContent = retVal;

  return;
}

function createClickRateLineGraph() {
  var ctx = document.getElementById("click-rate-over-time").getContext("2d");
  var currentCycle = JSON.parse(
    document.getElementById("currentCycle").innerText
  );
  console.log(currentCycle);
  var cycles = JSON.parse(document.getElementById("previousCycles").innerText);
  cycles.reverse();
  cycles.push(currentCycle);

  // The labels on the bottom axis - Cycle #1, Cycle #2, Cycle #3, etc.
  var labels = [];
  for (i = 0; i < cycles.length; i++) {
    labels.push(`Cycle #${i + 1}`);
  }

  var highData = [];
  var moderateData = [];
  var lowData = [];
  var allData = [];
  for (var i = 0; i < cycles.length; i++) {
    highData.push(getClickRateFromCycle(cycles[i], "high"));
    moderateData.push(getClickRateFromCycle(cycles[i], "moderate"));
    lowData.push(getClickRateFromCycle(cycles[i], "low"));
    allData.push(getClickRateFromCycle(cycles[i], "all"));
  }

  var datasets = [
    {
      label: "High",
      data: highData,
      borderColor: "#c41230",
      backgroundColor: "#c41230",
    },
    {
      label: "Moderate",
      data: moderateData,
      borderColor: "#0078ae",
      backgroundColor: "#0078ae",
    },
    {
      label: "Low",
      data: lowData,
      borderColor: "#5e9732",
      backgroundColor: "#5e9732",
    },
    {
      label: "All",
      data: allData,
      borderColor: "#5a5b5d",
      backgroundColor: "#5a5b5d",
    },
  ];

  const data = {
    labels: labels,
    datasets: datasets,
  };

  const options = {
    plugins: {
      legend: {
        display: true,
        position: "right",
      },
      datalabels: {
        font: {
          weight: "bold",
        },
        formatter: function (value, ctx) {
          return value + "%";
        },
        align: "top",
        offset: 4,
      },
    },
    scales: {
      y: {
        ticks: {
          callback: function (value, index, ticks) {
            return value + "%";
          },
          maxTicksLimit: 4,
          padding: 10,
        },
      },
    },
  };

  const chart = new Chart(ctx, {
    type: "line",
    data: data,
    options: options,
    plugins: [ChartDataLabels],
  });
}

function CapitalizeFirstLetter(input){
  return input.charAt(0).toUpperCase() + input.slice(1);
}

function getIndicatorClickedData(data,group){
  return data.filter(i => i['group'] == group).map(i => i['clicked']['ratio'] * 100)

}

//Not ideal but using chartjs requires some work arounds
function setStringLength(string,length){
  // console.log(length - string.length)
  console.log((' '.repeat(length - string.length) + string).length)
  return ' '.repeat(length - string.length) + string
}

function deceptionIndicatorBreakdownChart() {

  var behavior_ctx = document.getElementById("deception-indicator-breakdown-behavior").getContext("2d");
  var relevancy_ctx = document.getElementById("deception-indicator-breakdown-relevancy").getContext("2d");
  var sender_ctx = document.getElementById("deception-indicator-breakdown-sender").getContext("2d");
  var appearance_ctx = document.getElementById("deception-indicator-breakdown-appearance").getContext("2d");
  
  var cycleStats = JSON.parse(
    document.getElementById("currentCycle").innerText
  );
  var indicators = JSON.parse(
    document.getElementById("indicators").innerText
  );
  console.log(indicators)

  var indicatorStats = cycleStats.stats.indicator_stats;

  console.log(indicatorStats)

  var labels = [
    {display: 'Graphics - Visual Appeal', group:'appearance', indicator:'logo_graphics', label:'Visual Appeal'},
    {display: 'Graphics - Plain Text', group:'appearance', indicator:'logo_graphics', label:'Plain Text'},
    {display: 'Domain - Related/Spoofed', group:'appearance', indicator:'link_domain',label:'Related/Hidden/Spoofed'},
    {display: 'Domain - Unrelated', group:'appearance', indicator:'link_domain',label:'Unrelated'},
    {display: 'Proper Grammar', group:'appearance', indicator:'grammar', label:'Proper'},
    {display: 'Decent Grammar', group:'appearance', indicator:'grammar', label:'Decent'},
    {display: 'Poor Grammar', group:'appearance', indicator:'grammar', label:'Poor'},
    
    {display: 'Authoritative - Superior', group:'sender', indicator:'authoritative', label:'Superior'},
    {display: 'Authoritative - Peer', group:'sender', indicator:'authoritative', label:'Peer'},
    {display: 'Authoritative - None', group:'sender', indicator:'authoritative', label:'None'},
    {display: 'External - Specified', group:'sender', indicator:'external', label:'Specified'},
    {display: 'External - Unspecified', group:'sender', indicator:'external', label:'Not External/Unpsecified'},
    {display: 'Internal - Spoofed', group:'sender', indicator:'internal', label:'Spoofed'},
    {display: 'Internal - Generic', group:'sender', indicator:'internal', label:'Generic/Close'},
    {display: 'Internal - Unspecified', group:'sender', indicator:'internal', label:'Not Internal/Unspecified'},
    
    {display: 'Public News', group:'relevancy', indicator:'public_news', label:'Yes'},
    {display: 'Organization', group:'relevancy', indicator:'organization', label:'Yes'},
    
    {display: 'Greed', group:'behavior', indicator:'greed', label:'Yes'},
    {display: 'Fear', group:'behavior', indicator:'fear', label:'Yes'},
    {display: 'Curiosity', group:'behavior', indicator:'curiosity', label:'Yes'},
    {display: 'Duty or Obligation', group:'behavior', indicator:'duty_obligation', label:'Yes'},


  ]
  
  appearance_labels = []
  sender_labels = []
  relevancy_labels = []
  behavior_labels = []

  display_length = 0
  labels.forEach(label => {
    if(display_length < label['display'].length){
      display_length = label['display'].length
    }
  })

  labels.forEach(i => {
    if(i['group'] == 'appearance'){
      appearance_labels.push(i['display'])
    }
    else if(i['group'] == 'sender'){
      sender_labels.push(i['display'])
    }
    else if(i['group'] == 'relevancy'){
      relevancy_labels.push(i['display'])
    }
    else if(i['group'] == 'behavior'){
      behavior_labels.push(i['display'])
    }
  })
  console.log(appearance_labels)

  var dataset_sender = [   
    {
      label: "Sender",
      data: getIndicatorClickedData(indicatorStats,'sender'),
      borderColor: "#00FFFF",
      backgroundColor: "#4f76b0",
    },    
  ];
  var dataset_appearance = [   
    {
      label: "Appearance",
      data: getIndicatorClickedData(indicatorStats,'appearance'),
      borderColor: "#00FF00",
      backgroundColor: "#b7b7b7",
    },    
  ];
  var dataset_relevancy = [   
    {
      label: "Relevancy",
      data: getIndicatorClickedData(indicatorStats,'relevancy'),
      borderColor: "#00FF00",
      backgroundColor: "#e8844f",
    },    
  ];
  var dataset_behavior = [   
    {
      label: "Behavior",
      data: getIndicatorClickedData(indicatorStats,'behavior'),
      borderColor: "#00FF00",
      backgroundColor: "#705b94",
    },    
  ];

  const data_sender = {
    labels: sender_labels,
    datasets: dataset_sender,
  };
  const data_appearance = {
    labels: appearance_labels,
    datasets: dataset_appearance,
  };
  const data_relevancy = {
    labels: relevancy_labels,
    datasets: dataset_relevancy,
  };
  const data_behavior = {
    labels: behavior_labels,
    datasets: dataset_behavior,
  };

  let maxVal = 0
  indicatorStats.forEach(i => {
    if((i.clicked.ratio * 100) > maxVal){
      maxVal = i.clicked.ratio * 100
    }
  })
  
  options = {
    barThickness: 18,
    responsive: true,
    maintainAspectRatio: false,
    indexAxis: "y",
    layout:{
      padding:{
        right: 36,
        left: 30
      }
    },
    plugins: {
      legend: {
        display: false,
        position: "right",
      },
      datalabels: {
        align: 'end',
        anchor: 'end',       
        formatter: function (value, ctx) {
          return value + "%";
        },
      },
    },
    scales: {
      yAxes: {
        afterFit: function(scaleInstance) {
          scaleInstance.width = 170; // sets the width to 100px
        },
          grid: {
            drawBorder: false,
            color: function(context,i) {
              console.log(context)
            if(!context.tick){
              return
            }
            if (context.tick.value == 0) {
              return '#FFFFFF';
            }
            //else if (context.tick.value < 2) {
            //   return '#000000';
            // }
            return '#ffffff';
          }
        },
      },
      xAxes: {
        max: maxVal,
        ticks: {
          callback: function (value, index, ticks) {
            return value + "%";
          },
          maxTicksLimit: 7,
          minTicksLimit: 7,
        },
        grid: {
          drawBorder: false,
          color: function(context,i) {
            // console.log(context)
          if(!context.tick){
            // context.scale.ticks[context.scale.max].label = "TEST"
            // console.log(context.scale._maxLength)
            // context.scale._gridLineItems[0].color = "#FF0000"
            return
          }
          if (context.tick.value == maxVal) {
            return '#FFFFFF';
          } else {
            return '#000000';
          }
        }
      },
      },
    },
  };

  var xAxisLabelHeight = 20
  var rowHeight = 30
  var padding = 20

  document.getElementById("deception-indicator-breakdown-behavior").height = (rowHeight * 4) + padding
  document.getElementById("deception-indicator-breakdown-relevancy").height = (rowHeight * 2) + padding
  document.getElementById("deception-indicator-breakdown-sender").height = (rowHeight * 8) + padding
  document.getElementById("deception-indicator-breakdown-appearance").height = (rowHeight * 7) + xAxisLabelHeight
  
  new Chart(appearance_ctx, {
    type: "bar",
    data: data_appearance,
    options: options,
    plugins: [ChartDataLabels],
  });

  options.scales.xAxes.ticks.display = false
  options.layout ={
    padding: {
      right: 35,
      left: 30
    }
  },

  new Chart(behavior_ctx, {
    type: "bar",
    data: data_behavior,
    options: options,
    plugins: [ChartDataLabels],
  });
  new Chart(relevancy_ctx, {
    type: "bar",
    data: data_relevancy,
    options: options,
    plugins: [ChartDataLabels],
  });
  new Chart(sender_ctx, {
    type: "bar",
    data: data_sender,
    options: options,
    plugins: [ChartDataLabels],
  });
}