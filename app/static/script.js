document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('file_upload');
    const fileNameDisplay = document.getElementById('file_name_display');
    const form = document.getElementById('emailForm');
    const submitBtn = document.getElementById('submitBtn');
    const statusMsg = document.getElementById('status_message');

    let base64String = null;
    let originalFileName = null;

    // Handle File Selection and Base64 conversion
    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            fileNameDisplay.textContent = file.name;
            fileNameDisplay.style.color = 'var(--text-main)';
            originalFileName = file.name;

            const reader = new FileReader();
            reader.onload = function(event) {
                // Remove the data:MIME_TYPE;base64, part
                base64String = event.target.result.split(',')[1];
            };
            reader.readAsDataURL(file);
        } else {
            fileNameDisplay.textContent = "Attach a file (Optional)";
            fileNameDisplay.style.color = 'var(--text-muted)';
            base64String = null;
            originalFileName = null;
        }
    });

    // Handle form submit
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // UI Feedback: Loading state
        const originalBtnText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i data-feather="loader" class="spin"></i> <span>Processing...</span>';
        submitBtn.disabled = true;
        feather.replace(); // re-render icons
        statusMsg.classList.add('hidden');

        // Helper function for splitting emails
        const parseEmails = (str) => {
            if (!str) return [];
            return str.split(',').map(e => e.trim()).filter(e => e);
        };

        const toEmails = parseEmails(document.getElementById('to_email').value);
        const ccEmails = parseEmails(document.getElementById('cc_email').value);

        const payload = {
            to_email: toEmails.length === 1 ? toEmails[0] : toEmails,
            cc_email: ccEmails.length === 0 ? null : (ccEmails.length === 1 ? ccEmails[0] : ccEmails),
            subject: document.getElementById('subject').value,
            body: document.getElementById('body').value,
            smtp_user: document.getElementById('smtp_user').value,
            smtp_password: document.getElementById('smtp_password').value,
            smtp_host: document.getElementById('smtp_host').value,
            smtp_port: parseInt(document.getElementById('smtp_port').value, 10),
            smtp_tls: document.getElementById('smtp_tls').value === 'true'
        };

        if (base64String && originalFileName) {
            payload.attachment_base64 = base64String;
            payload.attachment_filename = originalFileName;
        }

        try {
            const response = await fetch('/send-email/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                const data = await response.json();
                showStatus('success', 'check-circle', `Email queued successfully! ID: ${data.task_id.substring(0,8)}...`);
                form.reset();
                fileNameDisplay.textContent = "Attach a file (Optional)";
                base64String = null;
            } else {
                const errorData = await response.json();
                showStatus('error', 'alert-circle', `Error: ${errorData.detail || 'Failed to queue email.'}`);
            }
        } catch (error) {
            showStatus('error', 'wifi-off', 'Cannot reach the server. Please check your connection.');
        } finally {
            // Restore button
            submitBtn.innerHTML = originalBtnText;
            submitBtn.disabled = false;
        }
    });

    function showStatus(type, icon, message) {
        statusMsg.className = `status-message status-${type}`;
        statusMsg.innerHTML = `<i data-feather="${icon}"></i> <span>${message}</span>`;
        feather.replace();
    }
    
    // Quick CSS for the spinner
    const style = document.createElement('style');
    style.innerHTML = `
        .spin { animation: spin 1s linear infinite; }
        @keyframes spin { 100% { transform: rotate(360deg); } }
    `;
    document.head.appendChild(style);

    // --- NEW TAB AND ENCRYPTION LOGIC ---

    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            
            btn.classList.add('active');
            document.getElementById(btn.dataset.target).classList.add('active');
        });
    });

    const encryptForm = document.getElementById('encryptForm');
    const encryptBtn = document.getElementById('encryptBtn');
    const encryptResult = document.getElementById('encrypt_result');

    if (encryptForm) {
        encryptForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const originalBtnText = encryptBtn.innerHTML;
            encryptBtn.innerHTML = '<i data-feather="loader" class="spin"></i> <span>Encrypting...</span>';
            encryptBtn.disabled = true;
            feather.replace();
            encryptResult.classList.add('hidden');

            const rawPassword = document.getElementById('raw_password').value;

            try {
                const response = await fetch('/encrypt/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ raw_password: rawPassword })
                });

                if (response.ok) {
                    const data = await response.json();
                    encryptResult.className = 'status-message status-success';
                    encryptResult.innerHTML = `
                        <div style="width: 100%">
                            <div style="margin-bottom: 8px; color: var(--text-main);"><i data-feather="check-circle" style="vertical-align: middle; margin-right: 5px;"></i><strong>Token Generated Successfully:</strong></div>
                            <div style="padding: 12px; background: rgba(0,0,0,0.3); border-radius: 8px; font-family: monospace; color: #f8f9fa; cursor: pointer; position: relative;" 
                                 title="Click to copy" 
                                 onclick="navigator.clipboard.writeText('${data.encrypted_token}'); alert('Token copied!');">
                                ${data.encrypted_token.match(/.{1,45}/g).join('<br>')}
                            </div>
                        </div>
                    `;
                    feather.replace();
                    encryptForm.reset();
                } else {
                    const errorData = await response.json();
                    encryptResult.className = 'status-message status-error';
                    encryptResult.innerHTML = `<i data-feather="alert-circle"></i> <span>Error: ${errorData.detail || 'Failed to encrypt'}</span>`;
                    feather.replace();
                }
            } catch (error) {
                encryptResult.className = 'status-message status-error';
                encryptResult.innerHTML = `<i data-feather="wifi-off"></i> <span>Connection Error</span>`;
                feather.replace();
            } finally {
                encryptBtn.innerHTML = originalBtnText;
                encryptBtn.disabled = false;
            }
        });
    }

    // Password Visibility Toggle
    const togglePassword = document.getElementById('togglePassword');
    const rawPasswordInput = document.getElementById('raw_password');

    if (togglePassword && rawPasswordInput) {
        togglePassword.addEventListener('click', () => {
            const type = rawPasswordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            rawPasswordInput.setAttribute('type', type);
            
            togglePassword.innerHTML = type === 'password' ? '<i data-feather="eye"></i>' : '<i data-feather="eye-off"></i>';
            feather.replace();
        });
    }

});
