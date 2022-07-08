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
  if (remainingMills > 1000) {
    seconds = Math.floor(remainingMills / 1000);
    retVal += seconds + " seconds.";
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
