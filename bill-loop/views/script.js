function main() {
  const markdownTab = document.getElementById("markdown-tab");
  const htmlTab = document.getElementById("html-tab");
  const markdownContent = document.getElementById("markdown-content");
  const htmlContent = document.getElementById("html-content");

  if (markdownTab && htmlTab && markdownContent && htmlContent) {
    const activeClasses = ["-mb-px", "border-b-2", "border-blue-500", "text-blue-500", "font-semibold"];
    const inactiveClasses = ["text-gray-500", "hover:text-blue-500", "font-semibold"];

    markdownTab.addEventListener("click", () => {
      markdownContent.classList.remove("hidden");
      htmlContent.classList.add("hidden");

      markdownTab.classList.add(...activeClasses);
      markdownTab.classList.remove(...inactiveClasses);

      htmlTab.classList.remove(...activeClasses);
      htmlTab.classList.add(...inactiveClasses);
    });

    htmlTab.addEventListener("click", () => {
      htmlContent.classList.remove("hidden");
      markdownContent.classList.add("hidden");

      htmlTab.classList.add(...activeClasses);
      htmlTab.classList.remove(...inactiveClasses);

      markdownTab.classList.remove(...activeClasses);
      markdownTab.classList.add(...inactiveClasses);
    });
  }
}

window.addEventListener("DOMContentLoaded", main);