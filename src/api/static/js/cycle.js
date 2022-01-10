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

function createClickRateLineGraph() {
  var ctx = document.getElementById("click-rate-over-time").getContext("2d");
  var currentCycle = JSON.parse(
    document.getElementById("currentCycle").innerText
  );
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
