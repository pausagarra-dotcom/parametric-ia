# SP-9: un missatge de l'app al xat, amb una captura, fet amb Claude Code local (sessio de Pau, sense clau d'API).
$here = "H:\Mi unidad\PARAMETRIC IA_New_shot\APP\recerca\sp9"
Remove-Item "$here\estat.json" -ErrorAction SilentlyContinue
$img = "H:\Mi unidad\PARAMETRIC IA_New_shot\APP\recerca\sp6\sp6_detall_Arctic.png"
$prompt = "Ets l'assistent d'una app de textures. Mira la captura $img (quadrats enfonsats sobre un cilindre). " +
          "L'usuari diu: 'els quadrats es veuen massa profunds, fes-los un 25% menys fondos'. " +
          "Llegeix l'estat amb l'eina llegir_estat, canvia el slider que toca amb canviar_parametre i respon en una frase."
$t = Measure-Command {
  $out = claude -p $prompt --mcp-config "$here\mcp_config.json" --strict-mcp-config `
         --allowedTools "Read,mcp__app__llegir_estat,mcp__app__canviar_parametre" --output-format json
}
$out | Set-Content "$here\prova_xat_resposta.json" -Encoding utf8
"temps total: {0:N1} s" -f $t.TotalSeconds
Get-Content "$here\estat.json"
