const app = {
    root: document.getElementById('app-root'),

    // Definição das Views (Páginas)
    views: {
        home: `
            <div class="view-container">
                <h1>Sistema de Votação Escolar</h1>
                <h2>A sua voz faz a diferença!</h2>
                <p>Participe das votações da escola de forma simples, segura e transparente.</p>
                <button class="btn btn-primary" onclick="app.navigate('login')">Acessar Votação</button>
                
                <div class="info-box">
                    <strong>Próxima Votação:</strong> Escolha do Grêmio Estudantil<br>
                    <strong>Data:</strong> 15 de Novembro de 2026<br>
                    <strong>Horário:</strong> 08h00 às 17h00
                </div>
            </div>
        `,
        login: `
            <div class="view-container">
                <h2>Autenticação de Eleitor</h2>
                <p>Insira suas credenciais para acessar a urna digital.</p>
                
                <div id="login-feedback" class="feedback-msg"></div>

                <form id="login-form" onsubmit="app.handleLogin(event)">
                    <div class="form-group">
                        <label for="ra">RA (Registro do Aluno)</label>
                        <input type="text" id="ra" placeholder="Digite seu RA" required>
                    </div>
                    <div class="form-group">
                        <label for="senha">Senha</label>
                        <input type="password" id="senha" placeholder="Digite sua senha" required>
                    </div>
                    
                    <button type="submit" class="btn btn-success">Entrar</button>
                    <button type="button" class="btn btn-secondary" onclick="app.navigate('home')">Voltar</button>
                </form>
            </div>
        `
    },

    // Roteador simples
    navigate: function(viewName) {
        if (this.views[viewName]) {
            this.root.innerHTML = this.views[viewName];
        } else {
            console.error("View não encontrada:", viewName);
        }
    },

    // Lógica de Autenticação (Mock para o MVP)
    handleLogin: function(event) {
        event.preventDefault();
        
        const ra = document.getElementById('ra').value;
        const senha = document.getElementById('senha').value;
        const feedbackEl = document.getElementById('login-feedback');
        
        // Simulação básica: Aceita apenas RA '12345' e senha '123'
        if (ra === '12345' && senha === '123') {
            feedbackEl.textContent = "Login realizado com sucesso! Redirecionando...";
            feedbackEl.className = "feedback-msg feedback-success";
            feedbackEl.style.display = "block";
            
            // Simula o redirecionamento após 2 segundos
            setTimeout(() => {
                alert("Redirecionando para as votações disponíveis...");
                this.navigate('home');
            }, 2000);
            
        } else {
            feedbackEl.textContent = "Erro: Verifique os dados informados.";
            feedbackEl.className = "feedback-msg feedback-error";
            feedbackEl.style.display = "block";
        }
    }
};

// Inicializa a aplicação na página Home
document.addEventListener("DOMContentLoaded", () => {
    app.navigate('home');
});