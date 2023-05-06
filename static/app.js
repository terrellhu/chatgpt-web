const submitButton = document.getElementById("submit");
const chatFileButton = document.getElementById("chatFile");
const uploadFileButton = document.getElementById("uploadFile");
const userIdInput = document.getElementById("userid");
const messageInput = document.getElementById("message");
const chatHistory = document.getElementById("chatHistory");

function appendMessageToChatHistory(message, source) {
  const messageElement = document.createElement("div");
  messageElement.innerText = source + ": " + message;
  // 将消息插入到聊天历史记录的最前面
  if (chatHistory.firstChild) {
    chatHistory.insertBefore(messageElement, chatHistory.firstChild);
  } else {
    // 如果聊天历史记录为空，则直接将消息元素添加为子元素
    chatHistory.appendChild(messageElement);
  }
}

submitButton.addEventListener("click", async () => {
  event.preventDefault();
  // 获取输入框的值
  const userid = userIdInput.value;
  const message = messageInput.value;

  if (!userid || !message) {
    return;
  }

  submitButton.disabled = true;
  appendMessageToChatHistory(message, "User");

  // 发送 POST 请求的逻辑
  const response = await fetch("/chat", {
    method: "POST",
    body: JSON.stringify({ userid, message }),
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (response.ok) {
    const data = await response.json();
    appendMessageToChatHistory(data.reply, "Chatbot");
  } else {
    console.error("Error sending message:", response.status, response.statusText);
  }

  // 重新启用按钮
  submitButton.disabled = false;

  messageInput.value = "";
});

// 按 Enter 键发送消息
messageInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();
    submitButton.click();
  }
});

chatFileButton.addEventListener("click", async () => {
  event.preventDefault();
  // 获取输入框的值
  const userid = userIdInput.value;
  const message = messageInput.value;

  if (!userid || !message) {
    return;
  }

  chatFileButton.disabled = true;
  appendMessageToChatHistory(message, "User");

  // 发送 POST 请求的逻辑
  const response = await fetch("/chat_file", {
    method: "POST",
    body: JSON.stringify({ userid, message }),
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (response.ok) {
    const data = await response.json();
    appendMessageToChatHistory(data.reply, "Chatbot");
  } else {
    console.error("Error sending message:", response.status, response.statusText);
  }

  chatFileButton.disabled = false;
  messageInput.value = "";
});

async function uploadFile() {
  const fileInput = document.getElementById("fileInput");
  const userid = document.getElementById("userid");

  const formData = new FormData();

  if (userid || fileInput.files.length > 0) {
    formData.append("file", fileInput.files[0]);
    formData.append("userid", userid.value)
  } else {
    alert("请填写用户id并选择一个文件");
    return;
  }

  uploadFileButton.disabled = true;
  const response = await fetch("/upload", {
    method: "POST",
    body: formData,
  });

  const responseData = await response.json();
  alert(responseData.message);
  uploadFileButton.disabled = false;
}

// 为上传按钮添加事件监听器
document.getElementById("uploadFile").addEventListener("click", uploadFile);