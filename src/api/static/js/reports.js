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
    labels: ["Sent", "Clicked"],
    datasets: [
      {
        data: [low_sent, low_clicked],
        backgroundColor: "#064875",
        barThickness: 40,
        label: "Low",
      },
      {
        data: [mod_sent, mod_clicked],
        backgroundColor: "#fcbf10",
        barThickness: 40,
        label: "Moderate",
      },
      {
        data: [high_sent, high_clicked],
        backgroundColor: "#007bc1",
        barThickness: 40,
        label: "High",
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
