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

function createStatsByLevelChart(
  chartId,
  low_sent,
  low_clicked,
  mod_sent,
  mod_clicked,
  high_sent,
  high_clicked
) {
  var ctx = document.getElementById(chartId).getContext("2d");
  const data = {
    labels: ["Emails Sent", "Unique Clicks"],
    datasets: [
      {
        data: [low_sent, low_clicked],
        backgroundColor: "#064875",
        barThickness: 40,
        label: "Low (1, 2)",
      },
      {
        data: [mod_sent, mod_clicked],
        backgroundColor: "#fcbf10",
        barThickness: 40,
        label: "Moderate (3, 4)",
      },
      {
        data: [high_sent, high_clicked],
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

function createClicksByDeceptionChart(chartId) {
  var ctx = document.getElementById(chartId).getContext("2d");
  var templateStats = JSON.parse(
    document.getElementById("templateStats").innerText
  );

  const sentStats = [];
  const clickStats = [];
  for (let i = 1; i <= 6; i++) {
    let templates = templateStats.filter(
      (obj) => obj.template.deception_score === i
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
        backgroundColor: "#336BFF",
        barThickness: 40,
        label: "Sent",
      },
      {
        data: clickStats,
        backgroundColor: "#D61317",
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
          stepSize: 200,
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
