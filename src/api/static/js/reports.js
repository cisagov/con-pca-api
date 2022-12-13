function createDoughnut(chartId, subtotal, total) {
  var ctx = document.getElementById(chartId).getContext("2d");
  const data = {
    datasets: [
      {
        data: [subtotal, total - subtotal],
        backgroundColor: ["#164A91", "#cecece"],
        borderWidth: 0,
        cutout: "65%",
        datalabels: {
          anchor: "end",
        },
      },
    ],
  };

  const options = {
    animation: false,
    plugins: {
      datalabels: {
        backgroundColor: function (context) {
          return context.dataset.backgroundColor;
        },
        borderColor: "white",
        borderRadius: 25,
        borderWidth: 2,
        color: "white",
        display: function (context) {
          var dataset = context.dataset;
          var value = dataset.data[context.dataIndex];
          return value > 0;
        },
        font: {
          weight: "bold",
        },
        padding: 6,
      },
    },
    // Core options
    aspectRatio: 1,
    layout: {
      padding: 15,
    },
  };

  const chart = new Chart(ctx, {
    type: "doughnut",
    data: data,
    options: options,
    plugins: [ChartDataLabels],
  });
  chart.canvas.parentNode.style.height = "115px";
  chart.canvas.parentNode.style.width = "130px";
}

function createStatsByLevelChart() {
  var ctx = document.getElementById("bar-stats-by-level").getContext("2d");
  var stats = JSON.parse(document.getElementById("overallStats").innerText);
  const data = {
    labels: ["Emails Sent", "Unique Clicks"],
    datasets: [
      {
        data: [stats.low.sent.count, stats.low.clicked.count],
        backgroundColor: "#064875",
        barThickness: 40,
        label: "Low (1, 2)",
      },
      {
        data: [stats.moderate.sent.count, stats.moderate.clicked.count],
        backgroundColor: "#fcbf10",
        barThickness: 40,
        label: "Moderate (3, 4)",
      },
      {
        data: [stats.high.sent.count, stats.high.clicked.count],
        backgroundColor: "#007bc1",
        barThickness: 40,
        label: "High (5, 6)",
      },
    ],
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

function createStatsByDeceptionChart() {
  var ctx = document.getElementById("bar-stats-by-deception").getContext("2d");
  var templateStats = JSON.parse(
    document.getElementById("templateStats").innerText,
  );

  const sentStats = [];
  const clickStats = [];
  for (let i = 1; i <= 6; i++) {
    let templates = templateStats.filter(
      (obj) => obj.template.deception_score === i,
    );
    let sent = 0;
    let clicked = 0;
    for (var j = 0; j < templates.length; j++) {
      sent += templates[j].sent.count;
      clicked += templates[j].clicked.count;
    }
    sentStats.push(sent);
    clickStats.push(clicked);
  }

  const data = {
    labels: [1, 2, 3, 4, 5, 6],
    datasets: [
      {
        data: sentStats,
        backgroundColor: "#164a91",
        barThickness: 40,
        label: "Sent",
      },
      {
        data: clickStats,
        backgroundColor: "#fdc010",
        barThickness: 40,
        label: "Clicked",
      },
    ],
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
      },
    },
    scales: {
      y: {
        ticks: {
          maxTicksLimit: 6,
        },
        title: {
          display: true,
          text: "Number Sent/Clicked",
        },
      },
      x: {
        title: {
          display: true,
          text: "Deception Level",
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

function clickRateTimeIntervalChart() {
  var ctx = document
    .getElementById("click-rate-time-interval")
    .getContext("2d");
  const timeStats = JSON.parse(
    document.getElementById("timeIntervalStats").innerText,
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

  const chart = new Chart(ctx, {
    type: "bar",
    data: data,
    options: options,
    plugins: [ChartDataLabels],
  });
}
