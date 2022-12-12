function createClickRateOverTime() {
  var ctx = document.getElementById("click-rate-over-time").getContext("2d");
  var currentCycle = JSON.parse(
    document.getElementById("currentCycle").innerText,
  );
  var previousCycles = JSON.parse(
    document.getElementById("previousCycles").innerText,
  );

  var labels = ["Low (1, 2)", "Moderate (3, 4)", "High (5, 6)"];
  var datasets = [
    {
      data: [
        (currentCycle.stats.stats.low.clicked.ratio * 100).toFixed(1),
        (currentCycle.stats.stats.moderate.clicked.ratio * 100).toFixed(1),
        (currentCycle.stats.stats.high.clicked.ratio * 100).toFixed(1),
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
            (previousCycles[i].stats.stats.low.clicked.ratio * 100).toFixed(1),
            (
              previousCycles[i].stats.stats.moderate.clicked.ratio * 100
            ).toFixed(1),
            (previousCycles[i].stats.stats.high.clicked.ratio * 100).toFixed(1),
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
  return (cycle.stats.stats[level].clicked.ratio * 100).toFixed(1);
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
          (clicked.one_minutes.ratio * 100).toFixed(1),
          (clicked.three_minutes.ratio * 100).toFixed(1),
          (clicked.five_minutes.ratio * 100).toFixed(1),
          (clicked.fifteen_minutes.ratio * 100).toFixed(1),
          (clicked.thirty_minutes.ratio * 100).toFixed(1),
          (clicked.sixty_minutes.ratio * 100).toFixed(1),
          (clicked.two_hours.ratio * 100).toFixed(1),
          (clicked.three_hours.ratio * 100).toFixed(1),
          (clicked.four_hours.ratio * 100).toFixed(1),
          (clicked.one_day.ratio * 100).toFixed(1),
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
    type: "line",
    data: data,
    options: options,
    plugins: [ChartDataLabels],
  });
}

function order_time_vals(time_vals) {
  ret_val = [];
  times_in_order = [
    "one_minutes",
    "three_minutes",
    "five_minutes",
    "fifteen_minutes",
    "thirty_minutes",
    "sixty_minutes",
    "two_hours",
    "three_hours",
    "four_hours",
    "one_day",
  ];
  times_in_order.forEach((t) => {
    ret_val.push(time_vals[t]["ratio"]);
  });
  return ret_val;
}

function clickingUserTimelineChart() {
  var ctx = document.getElementById("clicking-user-timeline").getContext("2d");

  var decep_stats = JSON.parse(
    document.getElementById("decep_level_stats").innerText,
  );

  labels = [
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
    // "2 day",
    // "3 day",
    // "4 day",
  ];

  dataset = [
    {
      label: "All",
      data: order_time_vals(decep_stats[9]["click_percentage_over_time"]),
      borderColor: "#5a5b5d",
      backgroundColor: "#5a5b5d",
    },
    {
      label: "Low",
      data: order_time_vals(decep_stats[6]["click_percentage_over_time"]),
      borderColor: "#5e9732",
      backgroundColor: "#5e9732",
    },
    {
      label: "Moderate",
      data: order_time_vals(decep_stats[7]["click_percentage_over_time"]),
      borderColor: "#0078ae",
      backgroundColor: "#0078ae",
    },
    {
      label: "High",
      data: order_time_vals(decep_stats[8]["click_percentage_over_time"]),
      borderColor: "#c41230",
      backgroundColor: "#c41230",
    },
  ];

  let data = {
    labels: labels,
    datasets: dataset,
  };
  let options = {
    responsive: true,
    plugins: {
      legend: {
        position: "bottom",
      },
      datalabels: {
        display: false,
        // align: 'end',
        // anchor: 'end',
      },
    },
    scales: {
      x: {
        title: {
          display: true,
          text: "Deception Level",
        },
      },
      y: {
        title: {
          display: true,
          text: "% of Unique Users",
        },
        min: 0,
        max: 1,
        ticks: {
          callback: function (value, index, ticks) {
            return value * 100 + "%";
          },
          stepSize: 0.25,
          // maxTicksLimit: 7,
        },
      },
    },
  };

  new Chart(ctx, {
    type: "line",
    data: data,
    options: options,
    plugins: [ChartDataLabels],
  });
}

function reportsToClickRatio() {
  var cycle = JSON.parse(document.getElementById("currentCycle").innerText);
  num = cycle.stats.stats.all.reported.count;
  denum = cycle.stats.stats.all.clicked.count;

  if (num == 0) {
    document.getElementById("reportsToClickRatio").textContent = "0";
    return;
  }

  if (!num || !denum) {
    document.getElementById("reportsToClickRatio").textContent = "N/A";
    return;
  }

  document.getElementById("reportsToClickRatio").textContent =
    (num / denum) * 100 + "%";
}

function avgTimeToFirstClick() {
  var currentCycle = JSON.parse(
    document.getElementById("currentCycle").innerText,
  );

  val = currentCycle.stats.stats.all.clicked.average;
  if (val == 0) {
    document.getElementById("avgTimeToFirtClick").textContent = "N/A";
    return;
  }

  document.getElementById("avgTimeToFirtClick").textContent =
    secondToTextDate(val);
}

function avgTimeToFirstReport() {
  var currentCycle = JSON.parse(
    document.getElementById("currentCycle").innerText,
  );

  val = currentCycle.stats.stats.all.reported.average;
  if (val === 0) {
    document.getElementById("avgTimeToFirtReport").textContent = "N/A";
    return;
  }

  document.getElementById("avgTimeToFirtReport").textContent =
    secondToTextDate(val);
}

function TimeIntervalText() {
  var currentCycle = JSON.parse(
    document.getElementById("currentCycle").innerText,
  );

  val = currentCycle.stats.stats.all.clicked.median;
  if (val == 0) {
    return "not found";
  }
  var retVal = "The median time to click was ";

  retVal += secondToTextDate(val);
  document.getElementById("timeIntervalClickInText").textContent = retVal;
}

function mostClickedTemplate() {
  var currentCycle = JSON.parse(
    document.getElementById("currentCycle").innerText,
  );

  most_clicked_template = currentCycle.stats.template_stats[0];
  currentCycle.stats.template_stats.forEach((t) => {
    if (most_clicked_template["clicked"]["count"] < t["clicked"]["count"]) {
      most_clicked_template = t;
    }
  });

  document.getElementById("mostClickedTemplate").textContent =
    most_clicked_template["template"]["name"];
}

function secondToTextDate(val) {
  var remainingSec = val;
  var days = 0;
  var hours = 0;
  var minutes = 0;
  var seconds = 0;

  retVal = "";
  //days
  if (remainingSec > 86400) {
    days = Math.floor(remainingSec / 86400);
    retVal += days + " days" + (remainingSec > 3600 ? ", " : ".");
    remainingSec = remainingSec % 86400;
  }
  //hours
  if (remainingSec > 3600) {
    hours = Math.floor(remainingSec / 3600);
    retVal += hours + " hours" + (remainingSec > 60 ? ", " : ".");
    remainingSec = remainingSec % 3600;
  }
  //minutes
  if (remainingSec > 60) {
    minutes = Math.floor(remainingSec / 60);
    remainingSec = remainingSec % 60;
    retVal += minutes + " minutes" + (remainingSec > 1 ? ", " : ".");
  }
  //seconds
  if (remainingSec > 1) {
    seconds = Math.floor(remainingSec / 1);
    retVal += seconds + " seconds.";
  }

  return retVal;
}

function createClickRateLineGraph() {
  var ctx = document.getElementById("click-rate-over-time").getContext("2d");
  var currentCycle = JSON.parse(
    document.getElementById("currentCycle").innerText,
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

function CapitalizeFirstLetter(input) {
  return input.charAt(0).toUpperCase() + input.slice(1);
}

function getIndicatorClickedData(data, group) {
  return data
    .filter((i) => i["group"] == group)
    .map((i) => i["clicked"]["ratio"] * 100);
}

//Not ideal but using chartjs requires some work arounds
function setStringLength(string, length) {
  // console.log(length - string.length)
  return " ".repeat(length - string.length) + string;
}

function deceptionIndicatorBreakdownChart() {
  var behavior_ctx = document
    .getElementById("deception-indicator-breakdown-behavior")
    .getContext("2d");
  var relevancy_ctx = document
    .getElementById("deception-indicator-breakdown-relevancy")
    .getContext("2d");
  var sender_ctx = document
    .getElementById("deception-indicator-breakdown-sender")
    .getContext("2d");
  var appearance_ctx = document
    .getElementById("deception-indicator-breakdown-appearance")
    .getContext("2d");

  var cycleStats = JSON.parse(
    document.getElementById("currentCycle").innerText,
  );
  var indicators = JSON.parse(document.getElementById("indicators").innerText);

  var indicatorStats = cycleStats.stats.indicator_stats;

  var labels = [
    {
      display: "Graphics - Visual Appeal",
      group: "appearance",
      indicator: "logo_graphics",
      label: "Visual Appeal",
    },
    {
      display: "Graphics - Plain Text",
      group: "appearance",
      indicator: "logo_graphics",
      label: "Plain Text",
    },
    {
      display: "Domain - Related/Spoofed",
      group: "appearance",
      indicator: "link_domain",
      label: "Related/Hidden/Spoofed",
    },
    {
      display: "Domain - Unrelated",
      group: "appearance",
      indicator: "link_domain",
      label: "Unrelated",
    },
    {
      display: "Proper Grammar",
      group: "appearance",
      indicator: "grammar",
      label: "Proper",
    },
    {
      display: "Decent Grammar",
      group: "appearance",
      indicator: "grammar",
      label: "Decent",
    },
    {
      display: "Poor Grammar",
      group: "appearance",
      indicator: "grammar",
      label: "Poor",
    },

    {
      display: "Authoritative - Superior",
      group: "sender",
      indicator: "authoritative",
      label: "Superior",
    },
    {
      display: "Authoritative - Peer",
      group: "sender",
      indicator: "authoritative",
      label: "Peer",
    },
    {
      display: "Authoritative - None",
      group: "sender",
      indicator: "authoritative",
      label: "None",
    },
    {
      display: "External - Specified",
      group: "sender",
      indicator: "external",
      label: "Specified",
    },
    {
      display: "External - Unspecified",
      group: "sender",
      indicator: "external",
      label: "Not External/Unpsecified",
    },
    {
      display: "Internal - Spoofed",
      group: "sender",
      indicator: "internal",
      label: "Spoofed",
    },
    {
      display: "Internal - Generic",
      group: "sender",
      indicator: "internal",
      label: "Generic/Close",
    },
    {
      display: "Internal - Unspecified",
      group: "sender",
      indicator: "internal",
      label: "Not Internal/Unspecified",
    },

    {
      display: "Public News",
      group: "relevancy",
      indicator: "public_news",
      label: "Yes",
    },
    {
      display: "Organization",
      group: "relevancy",
      indicator: "organization",
      label: "Yes",
    },

    { display: "Greed", group: "behavior", indicator: "greed", label: "Yes" },
    { display: "Fear", group: "behavior", indicator: "fear", label: "Yes" },
    {
      display: "Curiosity",
      group: "behavior",
      indicator: "curiosity",
      label: "Yes",
    },
    {
      display: "Duty or Obligation",
      group: "behavior",
      indicator: "duty_obligation",
      label: "Yes",
    },
  ];

  appearance_labels = [];
  sender_labels = [];
  relevancy_labels = [];
  behavior_labels = [];

  display_length = 0;
  labels.forEach((label) => {
    if (display_length < label["display"].length) {
      display_length = label["display"].length;
    }
  });

  labels.forEach((i) => {
    if (i["group"] == "appearance") {
      appearance_labels.push(i["display"]);
    } else if (i["group"] == "sender") {
      sender_labels.push(i["display"]);
    } else if (i["group"] == "relevancy") {
      relevancy_labels.push(i["display"]);
    } else if (i["group"] == "behavior") {
      behavior_labels.push(i["display"]);
    }
  });

  var dataset_sender = [
    {
      label: "Sender",
      data: getIndicatorClickedData(indicatorStats, "sender"),
      borderColor: "#00FFFF",
      backgroundColor: "#4f76b0",
    },
  ];
  var dataset_appearance = [
    {
      label: "Appearance",
      data: getIndicatorClickedData(indicatorStats, "appearance"),
      borderColor: "#00FF00",
      backgroundColor: "#b7b7b7",
    },
  ];
  var dataset_relevancy = [
    {
      label: "Relevancy",
      data: getIndicatorClickedData(indicatorStats, "relevancy"),
      borderColor: "#00FF00",
      backgroundColor: "#e8844f",
    },
  ];
  var dataset_behavior = [
    {
      label: "Behavior",
      data: getIndicatorClickedData(indicatorStats, "behavior"),
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

  let maxVal = 0;
  indicatorStats.forEach((i) => {
    if (i.clicked.ratio * 100 > maxVal) {
      maxVal = Math.floor(i.clicked.ratio * 100);
    }
  });

  options = {
    barThickness: 18,
    responsive: true,
    maintainAspectRatio: false,
    indexAxis: "y",
    layout: {
      padding: {
        right: 36,
        left: 30,
      },
    },
    plugins: {
      legend: {
        display: false,
        position: "right",
      },
      datalabels: {
        align: "end",
        anchor: "end",
        formatter: function (value, ctx) {
          return value + "%";
        },
      },
    },
    scales: {
      yAxes: {
        afterFit: function (scaleInstance) {
          scaleInstance.width = 170; // sets the width to 100px
        },
        grid: {
          drawBorder: false,
          color: function (context, i) {
            if (!context.tick) {
              return;
            }
            if (context.tick.value == 0) {
              return "#FFFFFF";
            }
            return "#ffffff";
          },
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
          color: function (context, i) {
            if (!context.tick) {
              return;
            }
            if (context.tick.value == maxVal) {
              return "#FFFFFF";
            } else {
              return "#000000";
            }
          },
        },
      },
    },
  };

  var xAxisLabelHeight = 20;
  var rowHeight = 30;
  var padding = 20;

  document.getElementById("deception-indicator-breakdown-behavior").height =
    rowHeight * 4 + padding;
  document.getElementById("deception-indicator-breakdown-relevancy").height =
    rowHeight * 2 + padding;
  document.getElementById("deception-indicator-breakdown-sender").height =
    rowHeight * 8 + padding;
  document.getElementById("deception-indicator-breakdown-appearance").height =
    rowHeight * 7 + xAxisLabelHeight;

  new Chart(appearance_ctx, {
    type: "bar",
    data: data_appearance,
    options: options,
    plugins: [ChartDataLabels],
  });

  options.scales.xAxes.ticks.display = false;
  (options.layout = {
    padding: {
      right: 35,
      left: 30,
    },
  }),
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

function clicksByDeceptionLevel() {
  var ctx = document
    .getElementById("clicks-by-deception-level")
    .getContext("2d");

  var decep_stats = JSON.parse(
    document.getElementById("decep_level_stats").innerText,
  );

  labels = ["1", "2", "3", "4", "5", "6"];

  dataset = [
    {
      label: "Unique Clicks",
      data: decep_stats.map((t) => t["unique_clicks"]),
      borderColor: "#456799",
      backgroundColor: "#456799",
    },
    {
      label: "Total Clicks",
      data: decep_stats.map((t) => t["total_clicks"]),
      borderColor: "#95433f",
      backgroundColor: "#95433f",
    },
    {
      label: "User Reports",
      data: decep_stats.map((t) => t["user_reports"]),
      borderColor: "#839752",
      backgroundColor: "#839752",
    },
  ];

  let data = {
    labels: labels,
    datasets: dataset,
  };
  let options = {
    responsive: true,
    plugins: {
      legend: {
        position: "bottom",
      },
      datalabels: {
        align: "end",
        anchor: "end",
      },
    },
    layout: {
      padding: {
        top: 20,
      },
    },
    scales: {
      x: {
        title: {
          display: true,
          text: "Deception Level",
        },
      },
      y: {
        title: {
          display: true,
          text: "Number of Clicks",
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

function formatTotalClicks(decep_stats, val) {
  ret_val = [];
  decep_stats.forEach((t) => {
    ret_val.push(t["unique_user_clicks"][val]);
  });
  return ret_val;
}

function totalClickCountByDeceptionLevel() {
  var ctx = document
    .getElementById("total-clicks-by-deception-level")
    .getContext("2d");

  var decep_stats = JSON.parse(
    document.getElementById("decep_level_stats").innerText,
  );

  var c = JSON.parse(document.getElementById("currentCycle").innerText);

  labels = ["1", "2", "3", "4", "5", "6"];

  dataset = [
    {
      label: "1 Click",
      data: formatTotalClicks(decep_stats, "one_click"),
      borderColor: "#456799",
      backgroundColor: "#456799",
    },
    {
      label: "2-3 Clicks",
      data: formatTotalClicks(decep_stats, "two_three_clicks"),
      borderColor: "#95433f",
      backgroundColor: "#95433f",
    },
    {
      label: "4-5 Clicks",
      data: formatTotalClicks(decep_stats, "four_five_clicks"),
      borderColor: "#839752",
      backgroundColor: "#839752",
    },
    {
      label: "6-10 Clicks",
      data: formatTotalClicks(decep_stats, "six_ten_clicks"),
      borderColor: "#705b94",
      backgroundColor: "#705b94",
    },
    {
      label: ">10 Clicks",
      data: formatTotalClicks(decep_stats, "ten_plus_clicks"),
      borderColor: "#5c9fbc",
      backgroundColor: "#5c9fbc",
    },
  ];

  let data = {
    labels: labels,
    datasets: dataset,
  };
  let options = {
    responsive: true,
    plugins: {
      legend: {
        position: "bottom",
      },
      datalabels: {
        align: "end",
        anchor: "end",
      },
    },
    layout: {
      padding: {
        top: 20,
      },
    },
    scales: {
      x: {
        title: {
          display: true,
          text: "Deception Level",
        },
      },
      y: {
        title: {
          display: true,
          text: "% of Unique Users",
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
