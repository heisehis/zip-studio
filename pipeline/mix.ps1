# Mixes the voiceover with a music bed (ducked under the voice) and/or a sound-effects track, then muxes with the silent render.
#   .\mix.ps1 -Project <dir> -Video <silent.mp4> -Out <final.mp4> [-Music <file>] [-MusicGain 0.30] [-MusicOffset 0] [-Sfx <wav>] [-Lufs -14]
# Loudness is normalised to -14 LUFS integrated (typical for short-form platforms), true peak -1.5 dBFS, AAC 48 kHz.
param([Parameter(Mandatory)][string]$Project, [Parameter(Mandatory)][string]$Video, [Parameter(Mandatory)][string]$Out,
      [string]$Music, [double]$MusicGain = 0.30, [double]$MusicOffset = 0, [string]$Sfx, [double]$Lufs = -14)
$tl = Get-Content (Join-Path $Project 'src\comp\timeline.js') -Raw
$tl = $tl.Split("`nTL.word")[0]; $dur = [double]($tl.Substring($tl.IndexOf('{'), $tl.LastIndexOf('}') - $tl.IndexOf('{') + 1) | ConvertFrom-Json).dur
$vo = Join-Path $Project 'src\audio\vo.wav'; $in = @('-i', $Video); $parts = @(); $n = 1; $fc = ''
if (Test-Path $vo) { $in += @('-i', $vo); $fc += "[$n`:a]aformat=channel_layouts=stereo,volume=1.6,asplit=2[vo][sc];"; $parts += '[vo]'; $voN = $n; $n++ }
if ($Music) {
  $in += @('-ss', $MusicOffset, '-i', $Music); $fc += "[$n`:a]aformat=channel_layouts=stereo,volume=$MusicGain[m0];"
  if ($voN) { $fc += "[m0][sc]sidechaincompress=threshold=0.02:ratio=8:attack=15:release=450[m];" } else { $fc += "[m0]anull[m];" }
  $parts += '[m]'; $n++
} elseif ($voN) { $fc += "[sc]anullsink;" }
if ($Sfx) { $in += @('-i', $Sfx); $fc += "[$n`:a]aformat=channel_layouts=stereo[s];"; $parts += '[s]'; $n++ }
if (-not $parts) { throw 'nothing to mix: no vo.wav, -Music or -Sfx' }
$fade = $dur - 1.6
$fc += ($parts -join '') + "amix=inputs=$($parts.Count):normalize=0:duration=longest,afade=t=out:st=${fade}:d=1.6,loudnorm=I=${Lufs}:TP=-1.5:LRA=11,aresample=48000[a]"
New-Item -ItemType Directory -Force (Split-Path $Out) | Out-Null
ffmpeg -hide_banner -loglevel error -y @in -filter_complex $fc -map 0:v -map '[a]' -c:v copy -c:a aac -b:a 192k -t $dur -movflags +faststart $Out
"duration $dur s -> $Out"
