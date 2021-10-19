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

  const oneScore = templateStats.filter(
    (obj) => obj.template.deception_score === 1
  );
  const twoScore = templateStats.filter(
    (obj) => obj.template.deception_score === 2
  );
  const threeScore = templateStats.filter(
    (obj) => obj.template.deception_score === 3
  );
  const fourScore = templateStats.filter(
    (obj) => obj.template.deception_score === 4
  );
  const fiveScore = templateStats.filter(
    (obj) => obj.template.deception_score === 5
  );
  const sixScore = templateStats.filter(
    (obj) => obj.template.deception_score === 6
  );

  // click scores

  const oneClickScore =
    (oneScore.reduce((sum, obj) => sum + obj.clicked.ratio, 0) /
      oneScore.length) *
    100;
  const twoClickScore =
    (twoScore.reduce((sum, obj) => sum + obj.clicked.ratio, 0) /
      twoScore.length) *
    100;
  const threeClickScore =
    (threeScore.reduce((sum, obj) => sum + obj.clicked.ratio, 0) /
      threeScore.length) *
    100;
  const fourClickScore =
    (threeScore.reduce((sum, obj) => sum + obj.clicked.ratio, 0) /
      fourScore.length) *
    100;
  const fiveClickScore =
    (fiveScore.reduce((sum, obj) => sum + obj.clicked.ratio, 0) /
      fiveScore.length) *
    100;
  const sixClickScore =
    (sixScore.reduce((sum, obj) => sum + obj.clicked.ratio, 0) /
      sixScore.length) *
    100;

  // open scores
  const oneOpenScore =
    (oneScore.reduce((sum, obj) => sum + obj.opened.ratio, 0) /
      oneScore.length) *
    100;
  const twoOpenScore =
    (twoScore.reduce((sum, obj) => sum + obj.opened.ratio, 0) /
      twoScore.length) *
    100;
  const threeOpenScore =
    (threeScore.reduce((sum, obj) => sum + obj.opened.ratio, 0) /
      threeScore.length) *
    100;
  const fourOpenScore =
    (fourScore.reduce((sum, obj) => sum + obj.opened.ratio, 0) /
      fourScore.length) *
    100;
  const fiveOpenScore =
    (fiveScore.reduce((sum, obj) => sum + obj.opened.ratio, 0) /
      fiveScore.length) *
    100;
  const sixOpenScore =
    (sixScore.reduce((sum, obj) => sum + obj.opened.ratio, 0) /
      sixScore.length) *
    100;

  const data = {
    labels: [1, 2, 3, 4, 5, 6],
    datasets: [
      {
        data: [
          oneClickScore,
          twoClickScore,
          threeClickScore,
          fourClickScore,
          fiveClickScore,
          sixClickScore,
        ],
        backgroundColor: "#336BFF",
        barThickness: 40,
        label: "Sent Rate",
      },
      {
        data: [
          oneOpenScore,
          twoOpenScore,
          threeOpenScore,
          fourOpenScore,
          fiveOpenScore,
          sixOpenScore,
        ],
        backgroundColor: "#D61317",
        barThickness: 40,
        label: "Click Rate",
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
          callback: function (value, index, values) {
            return value + "%";
          },
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
