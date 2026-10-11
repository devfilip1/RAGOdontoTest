# Atalhos para os comandos do projeto. Uso: .\run.ps1 <atalho> [argumentos]
# Os mesmos nomes existem no Makefile; um teste confere que os dois arquivos não divergem.

$Shortcuts = [ordered]@{
    "help"             = @("", "Lista os atalhos")
    "install"          = @("-m pip install -r requirements.txt", "Instala as dependências")
    "ingest"           = @("-m assistant.ingest", "Cria os índices de todas as estratégias")
    "chat"             = @("-m assistant.chat", "Conversa com o assistente")
    "test"             = @("-m pytest", "Testes de unidade (sem Ollama)")
    "test-integration" = @("-m pytest -m integration", "Testes com o Ollama e o índice")
    "eval"             = @("-m evaluation run --no-judge", "Avaliação da resposta, sem o juiz")
    "eval-smoke"       = @("-m evaluation run --smoke --no-judge", "Avaliação rápida, 10 perguntas")
    "eval-full"        = @("-m evaluation run", "Avaliação da resposta, com o juiz")
    "experiments"      = @("-m evaluation experiments", "Compara os experimentos de busca")
    "retrieval"        = @("-m evaluation retrieval", "Detalhe da busca do experimento do assistente")
    "kb-check"         = @("-m evaluation kb-check", "Verifica a base de conhecimento")
    "validate"         = @("-m evaluation validate", "Valida a configuração e o gabarito")
    "compare"          = @("-m evaluation compare", "Compara a última avaliação com a referência")
    "baseline"         = @("-m evaluation baseline set", "Marca a última avaliação como referência")
}

function Show-Shortcuts {
    Write-Host "Uso: .\run.ps1 <atalho> [argumentos]"
    Write-Host ""
    foreach ($name in $Shortcuts.Keys) {
        Write-Host ("  {0,-18} {1}" -f $name, $Shortcuts[$name][1])
    }
}

$name = if ($args.Count -gt 0) { $args[0] } else { "help" }
$rest = @($args | Select-Object -Skip 1)

if ($name -eq "help") {
    Show-Shortcuts
    exit 0
}

if (-not $Shortcuts.Contains($name)) {
    Write-Host "O atalho '$name' não existe."
    Write-Host ""
    Show-Shortcuts
    exit 2
}

$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    Write-Host "Ambiente virtual não encontrado. Crie com: python -m venv .venv"
    Write-Host "Depois instale as dependências: .\run.ps1 install"
    exit 1
}

Push-Location $PSScriptRoot
try {
    $command = $Shortcuts[$name][0] -split " "
    if ([Console]::IsInputRedirected) {
        $input | & $python @command @rest   # repassa a entrada quando o atalho recebe texto por pipe
    }
    else {
        & $python @command @rest
    }
    $code = $LASTEXITCODE
}
finally {
    Pop-Location
}
exit $code
