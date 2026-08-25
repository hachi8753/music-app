
document.addEventListener('DOMContentLoaded', () => {
    const buttons = document.querySelectorAll('.sidebar-list-name');
    const oscarBlock = document.querySelector('.oscar-block');

    buttons.forEach(button => {
        button.addEventListener('click', async () => {
            // activeボタンを強調
            buttons.forEach(b => b.classList.remove('active'));
            button.classList.add('active');

            try {

                const pageType = document.getElementById("list-page").dataset.pageType;
                const awardType = document.getElementById("list-page").dataset.awardType;
                let res;

                // FlaskのAPIからHTMLを取得（例: /awards/<award_id>）
                if (pageType == 'year') {
                    const year = button.getAttribute('data-year');
                    res = await fetch(`/oscar/update_block_year/${awardType}/${year}/`);
                } else if (pageType == 'category') {
                    const awardId = button.getAttribute('data-award-id');
                    res = await fetch(`/oscar/update_block_category/${awardId}/${awardType}`);
                }
                if (!res.ok) throw new Error("サーバー通信エラー");

                const html = await res.text();

                console.log(res)

                // メイン部分を更新
                oscarBlock.innerHTML = html;

                // スクロール位置を上に戻す
                oscarBlock.scrollIntoView({ behavior: 'smooth', block: 'start' });

            } catch (err) {
                console.error("エラー:", err);
                oscarBlock.innerHTML = `<p class="error">データを読み込めませんでした。</p>`;
            }
        });
    });
});



function openModal() {
    document.getElementById("modal").style.display = "block";
}

function closeModal() {
    document.getElementById("modal").style.display = "none";
}